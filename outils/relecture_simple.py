"""Page de relecture simplifiée pour Otsoa (vague 1 et suivantes).

Même contenu que relecture_otsoa.html (banc/relecture/tirage_aveugle.py, figé), présenté autrement :
une fiche à la fois, l'écart en tête, quatre questions guidées (motifs a à d de CONSIGNE_RELECTURE.md),
l'anglais replié. Ne lit du tirage que `numero` et `alerte_id` : aucun avis du premier relecteur n'entre
dans la page. Sortie : CSV fiche,reponse,motif, lu tel quel par banc/relecture/accord.py.

    python3 outils/relecture_simple.py experience/vague1/<horodatage>/relecture
"""
import html
import json
import sys
from pathlib import Path

GLOSSAIRE = {
    "item_ids": "articles", "new_item_ids": "nouveaux articles", "order_id": "commande",
    "payment_method_id": "moyen de paiement", "reason": "raison (texte)", "user_id": "client",
    "account_id": "compte", "credit_card_account_id": "compte de carte", "card_id": "carte",
    "requested_increase_amount": "montant demandé", "waive_early_closure_fee": "frais de clôture annulés",
    "address": "adresse", "date_of_birth": "date de naissance", "email": "e-mail", "name": "nom",
    "phone_number": "téléphone", "time_verified": "heure de vérification", "plot_type": "type de graphique",
    "time_min": "début de période", "time_max": "fin de période", "value_to_plot": "valeur tracée",
    "reservation_id": "réservation", "flights": "vols", "cabin": "classe", "passengers": "passagers",
    "amount": "montant", "subject": "objet (texte)", "body": "corps du message (texte)", "recipient": "destinataire",
}
NATURE = {
    "fausse": "ne correspond à aucune action attendue",
    "refusée": "a été refusée par l'outil",
    "doublon": "refait une action déjà faite",
}


def libelle(champ: str) -> str:
    base = champ.split("[")[0].split(".")[0]
    return GLOSSAIRE.get(base, "")


def fiche_vers_donnees(numero: int, d: dict) -> dict:
    diff = d.get("difference") or {}
    lignes = [dict(l, libelle=libelle(l["champ"])) for l in diff.get("lignes", [])]
    reg = d.get("reglement") or {}
    return {
        "numero": numero,
        "environnement": d["environnement"],
        "outil": (d.get("ecriture") or {}).get("outil", ""),
        "nature": NATURE.get(d.get("verdict_automatique", ""), d.get("verdict_automatique", "")),
        "verdict": d.get("verdict_automatique", ""),
        "encadre": d.get("encadre") or [],
        "attendue": diff.get("attendue", ""),
        "lignes": lignes,
        "note_diff": diff.get("note", ""),
        "resultat": d.get("resultat", ""),
        "consigne": d.get("consigne", ""),
        "regles": reg.get("paragraphes") or [],
        "regles_recherche": reg.get("recherche", ""),
        "reglement_entier": reg.get("texte_entier", ""),
        "etat_initial": d.get("etat_initial"),
        "attendues": d.get("attendues_lisibles") or [],
        "conversation": d.get("conversation") or [],
        "avertissements": d.get("avertissements") or [],
    }


def construire(dossier: Path) -> Path:
    tirage = json.loads((dossier / "tirage_aveugle.json").read_text(encoding="utf-8"))
    fiches = []
    for f in sorted(tirage["fiches"], key=lambda x: x["numero"]):
        d = json.loads((dossier / "fiches" / "aveugle" / f"{f['alerte_id']}.json").read_text(encoding="utf-8"))
        fiches.append(fiche_vers_donnees(f["numero"], d))
    cle = f"relecture-simple-{dossier.parent.name}-tour{tirage.get('tour', 1)}"
    donnees = json.dumps(fiches, ensure_ascii=False).replace("</", "<\\/")
    page = MODELE.replace("__DONNEES__", donnees).replace("__CLE__", html.escape(cle))
    sortie = dossier / "relecture_simple.html"
    sortie.write_text(page, encoding="utf-8")
    return sortie


MODELE = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relecture simplifiée</title>
<style>
:root{--fond:#f7f6f1;--texte:#1b1d1f;--discret:#5b6166;--ligne:#d7d5cc;--carte:#fff;--accent:#0d7a4f;--code:#efede5;--signal:#b26a00;--diff:#fde8d0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--fond:#16181a;--texte:#e8e6df;--discret:#9aa0a5;--ligne:#33373a;--carte:#1e2123;--accent:#4fd197;--code:#262a2c;--signal:#e0a040;--diff:#4a3418}}
*{box-sizing:border-box}body{margin:0;background:var(--fond);color:var(--texte);font:17px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:50rem;margin:0 auto;padding:1rem 16px 5rem}
h1{font-size:1.4rem;margin:.5rem 0}h2{font-size:1.15rem;margin:1.2rem 0 .4rem}
.carte{background:var(--carte);border:1px solid var(--ligne);border-radius:6px;padding:1rem;margin:1rem 0}
.barre{display:flex;gap:.3rem;flex-wrap:wrap;margin:.5rem 0}
.barre button{min-width:2.2rem;padding:.3rem;border:1px solid var(--ligne);background:var(--carte);color:var(--texte);border-radius:4px;cursor:pointer}
.barre button.fait{background:var(--accent);color:#fff;border-color:var(--accent)}
.barre button.ici{outline:3px solid var(--signal)}
table{border-collapse:collapse;width:100%;font-size:.95rem}th,td{border:1px solid var(--ligne);padding:.35rem .5rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}
tr.different td{background:var(--diff)}
code,pre{font:14px/1.45 ui-monospace,Menlo,Consolas,monospace}pre{background:var(--code);padding:.6rem;border-radius:4px;white-space:pre-wrap;overflow-wrap:anywhere}
details{border-top:1px solid var(--ligne);padding:.5rem 0}summary{cursor:pointer;font-weight:600}
.q{border:1px solid var(--ligne);border-radius:6px;padding:.7rem;margin:.6rem 0}
.q p{margin:.2rem 0}.q .aide{color:var(--discret);font-size:.92rem}
.q label{display:inline-block;margin:.3rem 1.2rem .1rem 0;cursor:pointer}
input[type=radio]{width:1.15rem;height:1.15rem;vertical-align:middle;margin-right:.35rem}
.verdict{font-size:1.1rem;font-weight:700;padding:.6rem;border-radius:6px;background:var(--code)}
.nav{display:flex;justify-content:space-between;gap:1rem;margin-top:1rem}
.nav button,.btn{font:inherit;padding:.6rem 1rem;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer}
.nav button[disabled]{opacity:.4;cursor:default}
.msg{margin:.3rem 0;padding:.4rem .6rem;border-radius:4px;background:var(--code)}
.msg.signale{border-left:5px solid var(--signal);background:var(--diff)}
.role{font-weight:600;color:var(--accent);margin-right:.4rem}
textarea{width:100%;min-height:8rem;font:14px ui-monospace,Menlo,monospace;background:var(--code);color:var(--texte);border:1px solid var(--ligne);padding:.5rem}
input[type=text]{width:100%;font:inherit;padding:.4rem;border:1px solid var(--ligne);border-radius:4px;background:var(--fond);color:var(--texte)}
.discret{color:var(--discret);font-size:.92rem}
</style></head><body><main>
<h1>Relecture : une fiche à la fois</h1>
<details class="carte"><summary>Ce qu'on te demande (à lire une fois)</summary>
<p>Dans chaque fiche, un agent a fait une action que le programme a <b>signalée</b> : elle ne colle pas avec ce que la tâche attendait.</p>
<p>Ta seule question : <b>est-ce une vraie erreur de l'agent, ou une fausse alerte ?</b></p>
<p>Ce n'est une fausse alerte que pour l'une de quatre raisons précises. Les quatre questions sous chaque fiche les passent en revue. Si tu réponds « non » aux quatre, c'est une vraie erreur. <b>Dans le doute, c'est une vraie erreur</b> (même règle que pour les autres relecteurs).</p>
<p>Commence par le cadre « L'écart » : souvent, c'est suffisant. Les sections repliées, en anglais, servent seulement à vérifier une question précise. Tu n'as pas à tout lire.</p>
<p>Tu ne vois ni l'avis du premier relecteur, ni le modèle de l'agent. Tes réponses sont gardées dans ce navigateur au fur et à mesure.</p>
</details>
<div class="barre" id="barre"></div>
<div id="fiche"></div>
<div class="nav"><button id="prec">← Précédente</button><button id="suiv">Suivante →</button></div>
<div class="carte" id="fin"><h2>Tes réponses</h2>
<p class="discret" id="compte"></p>
<textarea id="csv" readonly></textarea>
<p><button class="btn" id="copier">Copier le CSV</button> puis colle-le dans la conversation.</p></div>
</main>
<script>
const FICHES=__DONNEES__;const CLE="__CLE__";
const Q=[
 {m:"b",t:"Est-ce juste une autre façon d'écrire un texte libre ?",a:"Seulement si le champ différent est du texte (raison, message, objet) et que l'action garde le même destinataire, le même sens et le même effet. Ne vaut jamais pour un identifiant, un montant, une date ou un choix dans une liste."},
 {m:"c",t:"Le règlement permet-il ce que l'agent a fait, avec le résultat que voulait le client ?",a:"Il faut les deux : aucune règle ne l'interdit (et ses conditions sont remplies), et le client obtient ce qu'il demandait dans sa consigne. Où vérifier : « Règles utiles » et « Ce que le client voulait »."},
 {m:"a",t:"La tâche elle-même est-elle fausse ?",a:"Seulement si ses propres pièces se contredisent : l'action attendue est interdite par le règlement, impossible avec les données, contraire à la consigne du client, ou demande une information introuvable. Une tâche difficile n'est pas fausse."},
 {m:"d",t:"Notre programme s'est-il trompé en comparant ?",a:"L'action est juste, mais la comparaison est mal faite : même valeur écrite autrement, champ qui n'aurait pas dû être comparé, refus causé par notre banc et pas par l'agent."}
];
let R={};try{R=JSON.parse(localStorage.getItem(CLE)||"{}")}catch(e){}
function sauver(){try{localStorage.setItem(CLE,JSON.stringify(R))}catch(e){}majFin();majBarre()}
let i=0;
const e=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function verdictDe(r){if(!r)return null;for(const q of Q){const v=r[q.m];if(v==="oui")return{rep:"fausse alerte",motif:q.m};if(v!=="non")return null}return{rep:"vraie erreur",motif:""}}
function rendre(){
 const f=FICHES[i],r=R[f.numero]||{};
 const lignes=f.lignes.map(l=>`<tr class="${l.etat==="identique"?"":"different"}"><td><code>${e(l.champ)}</code>${l.libelle?`<br><span class="discret">${e(l.libelle)}</span>`:""}</td><td><code>${e(l.agent)}</code></td><td><code>${e(l.attendu)}</code></td><td>${e(l.etat)}${l.libre?" · texte libre":""}${l.compare===false?" · non comparé":""}</td></tr>`).join("");
 const diffs=f.lignes.filter(l=>l.etat!=="identique").length;
 let h=`<div class="carte"><h2>Fiche ${f.numero} sur ${FICHES.length} · ${e(f.environnement)}</h2>
 <p>L'agent a utilisé l'outil <code>${e(f.outil)}</code>. Le programme l'a signalée parce qu'elle <b>${e(f.nature)}</b>.</p>
 <h2>L'écart</h2>`;
 if(f.lignes.length){h+=`<p class="discret">Comparaison avec l'action attendue la plus proche. Les lignes colorées diffèrent (${diffs}).</p><div style="overflow-x:auto"><table><tr><th>Champ</th><th>Agent</th><th>Attendu</th><th>État</th></tr>${lignes}</table></div>`}
 else{h+=`<p class="discret">Pas de comparaison champ par champ pour cette fiche.</p>`}
 if(f.note_diff)h+=`<p class="discret">${e(f.note_diff)}</p>`;
 if(f.avertissements.length)h+=`<p><b>Avertissement du programme :</b> ${f.avertissements.map(e).join(" ; ")}</p>`;
 h+=`<details><summary>Résumé complet du programme (français)</summary><ul>${f.encadre.map(x=>`<li>${e(x)}</li>`).join("")}</ul></details></div>`;
 h+=`<div class="carte"><h2>Pour vérifier (en anglais, ouvre seulement ce qui sert)</h2>
 <details><summary>Ce que le client voulait (sa consigne)</summary><pre>${e(f.consigne)}</pre></details>
 <details><summary>Règles utiles pour cet outil</summary>${f.regles.length?f.regles.map(p=>`<p class="discret">${e(p.section)}</p><pre>${e(p.texte)}</pre>`).join(""):`<p class="discret">Aucune règle repérée (${e(f.regles_recherche)}).</p>`}</details>
 <details><summary>Actions attendues par la tâche</summary><pre>${e(f.attendues.join("\n"))}</pre></details>
 <details><summary>Ce que l'outil a répondu à l'agent</summary><pre>${e(f.resultat)}</pre></details>
 ${f.etat_initial?`<details><summary>Données de départ propres à la tâche</summary><pre>${e(typeof f.etat_initial==="string"?f.etat_initial:JSON.stringify(f.etat_initial,null,1))}</pre></details>`:""}
 <details id="conv"><summary>Conversation entière (l'action signalée est surlignée)</summary>${f.conversation.map(m=>`<div class="msg${m.signale?" signale":""}"${m.signale?' id="signalee"':""}><span class="role">${e(m.role)}</span>${m.signale?"<b>ACTION SIGNALÉE</b> ":""}<span style="white-space:pre-wrap">${e(m.texte)}</span></div>`).join("")}</details>
 <details><summary>Règlement entier</summary><pre>${e(f.reglement_entier)}</pre></details></div>`;
 h+=`<div class="carte"><h2>Tes quatre questions</h2><p class="discret">Dans l'ordre. Dès qu'un « oui » est prouvé par les pièces, c'est une fausse alerte : les questions suivantes ne servent plus.</p>`;
 let stop=false;
 Q.forEach((q,k)=>{const v=r[q.m]||"";h+=`<div class="q"${stop?' style="opacity:.4"':""}><p><b>${k+1}. ${q.t}</b></p><p class="aide">${q.a}</p>
 <label><input type="radio" name="q${q.m}" value="oui" ${v==="oui"?"checked":""} ${stop?"disabled":""}>oui</label>
 <label><input type="radio" name="q${q.m}" value="non" ${v==="non"?"checked":""} ${stop?"disabled":""}>non</label></div>`;if(v==="oui")stop=true});
 const vd=verdictDe(r);
 h+=`<p class="verdict">${vd?(vd.rep==="vraie erreur"?"→ Vraie erreur":"→ Fausse alerte (motif "+vd.motif+")"):"→ Pas encore de réponse"}</p>
 <p><label for="note">Ta raison en quelques mots (facultatif)</label><input type="text" id="note" value="${e(r.note||"")}"></p></div>`;
 document.getElementById("fiche").innerHTML=h;
 document.querySelectorAll('#fiche input[type=radio]').forEach(el=>el.onchange=()=>{const m=el.name.slice(1);const x=R[f.numero]||{};x[m]=el.value;
   if(el.value==="oui"){let apres=false;for(const q of Q){if(apres)delete x[q.m];if(q.m===m)apres=true}}R[f.numero]=x;sauver();rendre()});
 document.getElementById("note").oninput=ev=>{const x=R[f.numero]||{};x.note=ev.target.value;R[f.numero]=x;sauver()};
 document.getElementById("prec").disabled=i===0;document.getElementById("suiv").disabled=i===FICHES.length-1;majBarre();
}
function majBarre(){document.getElementById("barre").innerHTML=FICHES.map((f,k)=>`<button class="${verdictDe(R[f.numero])?"fait":""} ${k===i?"ici":""}" data-k="${k}">${f.numero}</button>`).join("");
 document.querySelectorAll("#barre button").forEach(b=>b.onclick=()=>{i=+b.dataset.k;rendre();scrollTo(0,0)})}
function majFin(){let n=0;const L=["fiche,reponse,motif"];for(const f of FICHES){const v=verdictDe(R[f.numero]);if(!v)continue;n++;const note=(R[f.numero].note||"").replace(/"/g,"'");
 L.push(`${f.numero},${v.rep},"${v.motif?v.motif+(note?" : "+note:""):note}"`)}
 document.getElementById("csv").value=L.join("\n");document.getElementById("compte").textContent=`${n} fiche(s) sur ${FICHES.length} répondues.`+(n<FICHES.length?" Il en manque.":"")}
document.getElementById("prec").onclick=()=>{i--;rendre();scrollTo(0,0)};
document.getElementById("suiv").onclick=()=>{i++;rendre();scrollTo(0,0)};
document.getElementById("copier").onclick=async()=>{const t=document.getElementById("csv");try{await navigator.clipboard.writeText(t.value)}catch(err){t.select();document.execCommand("copy")}};
rendre();majFin();
</script></body></html>
"""

if __name__ == "__main__":
    print(construire(Path(sys.argv[1])))
