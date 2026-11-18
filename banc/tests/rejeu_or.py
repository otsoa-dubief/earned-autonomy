"""Aide aux tests : transforme les actions ATTENDUES (gold) des quatre bancs en
enregistrements au format de verdicts.py, comme si un agent parfait les avait
jouees.

Pour l'aviation et le commerce, le montant n'est pas dans les arguments : on
rejoue a la main, en Python pur et sans importer le code des bancs, l'effet de
chaque outil sur l'etat initial (db.json) pour fabriquer l'objet que l'outil
renvoie (reservation, commande). C'est la meme formule que le code du banc,
relue ligne a ligne. Un enchainement sur une meme reservation ou commande est
rejoue dans l'ordre. Pour la banque, les arguments suffisent, sauf le releve
de limite (rien dans le resultat fabrique : montant illisible, plafonne).

Aucune trajectoire ni aucun resultat d'agent n'est lu : seulement db.json,
tasks.json et les CSV de taches.
"""
import ast
import copy
import csv
import json
from pathlib import Path

import verdicts as v


def _tache_actions(t):
    ec = t.get("evaluation_criteria") or {}
    return [a for a in (ec.get("actions") or []) if a.get("requestor", "assistant") != "user"]


# ---------------------------------------------------------------------------
# aviation
# ---------------------------------------------------------------------------
def _rejeu_airline(db, actions):
    res = copy.deepcopy(db["reservations"])
    flights = db["flights"]
    sorties = []
    for a in actions:
        n, ar = a["name"], a.get("arguments") or {}
        contenu = "ok"
        r = res.get(ar.get("reservation_id"))
        if n == "get_reservation_details" and r is not None:
            contenu = json.dumps(r)
        elif n == "book_reservation":
            contenu = json.dumps({"reservation_id": "NEW001", "payment_history": ar["payment_methods"], "status": None})
        elif n == "cancel_reservation" and r is not None:
            ref = [{"payment_id": p["payment_id"], "amount": -p["amount"]} for p in r["payment_history"]]
            r["payment_history"].extend(ref)
            r["status"] = "cancelled"
            contenu = json.dumps(r)
        elif n == "update_reservation_flights" and r is not None:
            npax = len(r["passengers"])
            total = 0
            nouveaux = []
            for f in ar["flights"]:
                m = [x for x in r["flights"] if x["flight_number"] == f["flight_number"]
                     and x["date"] == f["date"] and ar["cabin"] == r["cabin"]]
                if m:
                    total += m[0]["price"] * npax
                    nouveaux.append(m[0])
                else:
                    prix = flights[f["flight_number"]]["dates"][f["date"]]["prices"][ar["cabin"]]
                    total += prix * npax
                    nouveaux.append({"flight_number": f["flight_number"], "date": f["date"], "price": prix})
            total -= sum(x["price"] for x in r["flights"]) * npax
            if total != 0:
                r["payment_history"].append({"payment_id": ar["payment_id"], "amount": total})
            r["flights"] = nouveaux
            r["cabin"] = ar["cabin"]
            contenu = json.dumps(r)
        elif n == "update_reservation_baggages" and r is not None:
            frais = 50 * max(0, ar["nonfree_baggages"] - r["nonfree_baggages"])
            if frais != 0:
                r["payment_history"].append({"payment_id": ar["payment_id"], "amount": frais})
            r["total_baggages"] = ar["total_baggages"]
            r["nonfree_baggages"] = ar["nonfree_baggages"]
            contenu = json.dumps(r)
        elif n == "update_reservation_passengers" and r is not None:
            r["passengers"] = ar["passengers"]
            contenu = json.dumps(r)
        elif n == "send_certificate":
            contenu = f"Certificate certificate_9 added to user {ar['user_id']} with amount {ar['amount']}."
        sorties.append(contenu)
    return sorties


# ---------------------------------------------------------------------------
# commerce
# ---------------------------------------------------------------------------
def _rejeu_retail(db, actions):
    orders = copy.deepcopy(db["orders"])
    prods = db["products"]
    sorties = []
    for a in actions:
        n, ar = a["name"], a.get("arguments") or {}
        contenu = "ok"
        o = orders.get(ar.get("order_id"))
        if o is not None and n == "cancel_pending_order":
            ref = [{"transaction_type": "refund", "amount": p["amount"], "payment_method_id": p["payment_method_id"]}
                   for p in o["payment_history"]]
            o["payment_history"].extend(ref)
            o["status"] = "cancelled"
            contenu = json.dumps(o)
        elif o is not None and n in ("exchange_delivered_order_items", "modify_pending_order_items"):
            diff = 0
            for iid, nid in zip(ar["item_ids"], ar["new_item_ids"]):
                it = next(i for i in o["items"] if i["item_id"] == iid)
                diff += prods[it["product_id"]]["variants"][nid]["price"] - it["price"]
            diff = round(diff, 2)
            if n == "exchange_delivered_order_items":
                o["status"] = "exchange requested"
                o["exchange_items"] = sorted(ar["item_ids"])
                o["exchange_new_items"] = sorted(ar["new_item_ids"])
                o["exchange_payment_method_id"] = ar["payment_method_id"]
                o["exchange_price_difference"] = diff
            else:
                o["payment_history"].append({
                    "transaction_type": "payment" if diff > 0 else "refund",
                    "amount": abs(diff), "payment_method_id": ar["payment_method_id"]})
                o["status"] = "pending (item modified)"
            contenu = json.dumps(o)
        elif o is not None and n == "modify_pending_order_payment":
            amt = o["payment_history"][0]["amount"]
            ancien = o["payment_history"][0]["payment_method_id"]
            o["payment_history"].extend([
                {"transaction_type": "payment", "amount": amt, "payment_method_id": ar["payment_method_id"]},
                {"transaction_type": "refund", "amount": amt, "payment_method_id": ancien}])
            contenu = json.dumps(o)
        elif o is not None and n == "return_delivered_order_items":
            o["status"] = "return requested"
            o["return_items"] = sorted(ar["item_ids"])
            o["return_payment_method_id"] = ar["payment_method_id"]
            contenu = json.dumps(o)
        elif o is not None and n == "modify_pending_order_address":
            o["address"] = {k: ar.get(k) for k in ("address1", "address2", "city", "country", "state", "zip")}
            contenu = json.dumps(o)
        sorties.append(contenu)
    return sorties


# ---------------------------------------------------------------------------
# construction des parties
# ---------------------------------------------------------------------------
def enregistrements_tau2(racine, domaine):
    racine = Path(racine)
    types = v.types_tau2(racine, domaine)
    taches = v.charger_taches_tau2(racine, domaine, types)
    dossier = racine / "data" / "tau2" / "domains" / domaine
    brut = json.loads((dossier / "tasks.json").read_text(encoding="utf-8"))
    db = json.loads((dossier / "db.json").read_text(encoding="utf-8")) if domaine != "banking_knowledge" else None
    lignes = []
    for t in brut:
        actions = _tache_actions(t)
        if domaine == "airline":
            contenus = _rejeu_airline(db, actions)
        elif domaine == "retail":
            contenus = _rejeu_retail(db, actions)
        else:
            contenus = ["ok"] * len(actions)
        msgs = []
        for i, (a, c) in enumerate(zip(actions, contenus)):
            msgs.append({"role": "assistant", "content": None, "tool_calls": [
                {"id": f"c{i}", "name": a["name"], "arguments": a.get("arguments") or {}}]})
            msgs.append({"role": "tool", "id": f"c{i}", "content": c})
        run = {"id": f"gold-{t['id']}", "task_id": t["id"], "messages": msgs}
        lignes.extend(v.actions_partie_tau2(run, taches, types, domaine, "gold"))
    return lignes


def enregistrements_workbench(racine):
    racine = Path(racine)
    types = v.types_workbench(racine)
    taches = v.charger_taches_workbench(racine)
    dossier = racine / "data" / "processed" / "tasks_and_outcomes"
    lignes = []
    for chemin in sorted(dossier.glob("*_tasks_and_outcomes.csv")):
        prefixe = chemin.name[: -len("_tasks_and_outcomes.csv")]
        with open(chemin, newline="", encoding="utf-8") as fh:
            for i, ligne in enumerate(csv.DictReader(fh)):
                chaines = ast.literal_eval(ligne["outcome"])
                game = {"id": f"gold-{prefixe}-{i}", "tache": f"{prefixe}:{i}", "appels": list(chaines), "modele": "gold"}
                lignes.extend(v.actions_partie_workbench(game, taches, types))
    return lignes
