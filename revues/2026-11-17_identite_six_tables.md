# Identité des six tables des deux passages du rejeu final (vérification indépendante, 17/11/2026)

Méthode : empreintes SHA-256 seulement (`shasum -a 256`), aucun contenu lu. Passage 1 = manifeste `experience/rejeu_final_echec_1_SHA256.txt` ; passage 2 = fichiers présents dans `experience/rejeu_final/`.

| fichier | empreinte passage 1 | empreinte passage 2 | identique |
|---|---|---|---|
| budget.csv | 48f8e3375b5ac080ece8cdf7ff3bc0fb140502d820e3a6509ba328c7d30b1fa3 | 48f8e3375b5ac080ece8cdf7ff3bc0fb140502d820e3a6509ba328c7d30b1fa3 | oui |
| charges.csv | 68ccb7a9372865af8c2b8b40a216d268c11b2aa343940f835d66d97c9cb4b7f1 | 68ccb7a9372865af8c2b8b40a216d268c11b2aa343940f835d66d97c9cb4b7f1 | oui |
| derive.csv | 2cd6f44a06c7a623fc49eadb947d896c493e89fe043fba263492736e551d934c | 2cd6f44a06c7a623fc49eadb947d896c493e89fe043fba263492736e551d934c | oui |
| ecart.csv | f18d20a6fdeebbfe283efac8b80c8b5fd053cd3ff123c1663c85155d612ae475 | f18d20a6fdeebbfe283efac8b80c8b5fd053cd3ff123c1663c85155d612ae475 | oui |
| garantie.csv | ecffc34839c069394f9bf24339b4db3370ce6b4003f70084addda5011e674729 | ecffc34839c069394f9bf24339b4db3370ce6b4003f70084addda5011e674729 | oui |
| retrait.csv | b992c7016430c26197d31b66cfe30c9c0bc4d4f8a1948001a8dfcf8bd75102db | b992c7016430c26197d31b66cfe30c9c0bc4d4f8a1948001a8dfcf8bd75102db | oui |

Conclusion : les six tables des deux passages sont identiques octet pour octet (six empreintes concordantes).
