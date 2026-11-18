# Niveau du max-T de B-tout : sorties de `maxt_niveau.py`

| Régime | Formule | Répétitions | Au moins un dépassement établi | Part | IC 95 % (Wilson) | Pire cellule seule |
|---|---|---|---|---|---|---|
| N1 | F0 | 200 | 31 | 15.5 % | 11.1–21.2 % | 1/3 (scenario/WorkBench/claude-opus-5-5/claude-sonnet-5-5/annoncé faible) |
| N1 | F1 | 200 | 10 | 5.0 % | 2.7–9.0 % | 32/200 (scenario/WorkBench/claude-haiku-5-5/claude-opus-5-5/annoncé faible) |
| N1 | F2 | 200 | 30 | 15.0 % | 10.7–20.6 % | 32/200 (scenario/WorkBench/claude-opus-5-5/claude-haiku-5-5/silencieux faible) |
| N1 | F3 | 200 | 6 | 3.0 % | 1.4–6.4 % | 27/200 (config/WorkBench/claude-haiku-5-5 faible) |
| N1 | F4 | 200 | 18 | 9.0 % | 5.8–13.8 % | 10/200 (scenario/WorkBench/claude-sonnet-5-5/claude-haiku-5-5/annoncé faible) |
| N2 | F0 | 100 | 3 | 3.0 % | 1.0–8.5 % | 33/100 (scenario/banque/claude-opus-5-5/claude-haiku-5-5/silencieux faible) |
| N2 | F1 | 100 | 1 | 1.0 % | 0.2–5.4 % | 12/100 (scenario/banque/claude-haiku-5-5/claude-sonnet-5-5/silencieux faible) |
| N2 | F2 | 100 | 9 | 9.0 % | 4.8–16.2 % | 13/100 (scenario/banque/claude-sonnet-5-5/claude-haiku-5-5/silencieux faible) |
| N2 | F3 | 100 | 0 | 0.0 % | 0.0–3.7 % | 1/12 (scenario/WorkBench/claude-opus-5-5/claude-sonnet-5-5/silencieux faible) |
| N2 | F4 | 100 | 8 | 8.0 % | 4.1–15.0 % | 1/13 (scenario/aviation/claude-sonnet-5-5/claude-haiku-5-5/silencieux moyen) |
| P3 | F0 | 100 | 100 | 100.0 % | 96.3–100.0 % |  |
| P3 | F1 | 100 | 100 | 100.0 % | 96.3–100.0 % |  |
| P3 | F2 | 100 | 100 | 100.0 % | 96.3–100.0 % |  |
| P3 | F3 | 100 | 100 | 100.0 % | 96.3–100.0 % |  |
| P3 | F4 | 100 | 100 | 100.0 % | 96.3–100.0 % |  |
| P2 | F0 | 120 | 1 | 0.8 % | 0.1–4.6 % |  |
| P2 | F1 | 120 | 0 | 0.0 % | 0.0–3.1 % |  |
| P2 | F2 | 120 | 2 | 1.7 % | 0.5–5.9 % |  |
| P2 | F3 | 120 | 0 | 0.0 % | 0.0–3.1 % |  |
| P2 | F4 | 120 | 0 | 0.0 % | 0.0–3.1 % |  |
| P1 | F0 | 60 | 3 | 5.0 % | 1.7–13.7 % |  |
| P1 | F1 | 60 | 2 | 3.3 % | 0.9–11.4 % |  |
| P1 | F2 | 60 | 2 | 3.3 % | 0.9–11.4 % |  |
| P1 | F3 | 60 | 1 | 1.7 % | 0.3–8.9 % |  |
| P1 | F4 | 60 | 0 | 0.0 % | 0.0–6.0 % |  |
| P4 | F0 | 30 | 30 | 100.0 % | 88.6–100.0 % |  |
| P4 | F1 | 30 | 30 | 100.0 % | 88.6–100.0 % |  |
| P4 | F2 | 30 | 30 | 100.0 % | 88.6–100.0 % |  |
| P4 | F3 | 30 | 30 | 100.0 % | 88.6–100.0 % |  |
| P4 | F4 | 30 | 30 | 100.0 % | 88.6–100.0 % |  |

Formules acceptables : F1, F3.
**Formule retenue par la règle (section 4) : F1** (acceptable (au plus 5 % observés en N1, N2 et P2), la plus puissante).
