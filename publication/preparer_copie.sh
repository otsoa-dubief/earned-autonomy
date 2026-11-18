#!/bin/sh
# Builds the clean publication snapshot outside the working repository (PLAN_SUITE T48). Usage: sh publication/preparer_copie.sh DEST
set -e
SRC=$(cd "$(dirname "$0")/.." && pwd); DEST=$1
[ -n "$DEST" ] && [ ! -e "$DEST" ] || { echo "DEST must be a new path"; exit 1; }
mkdir -p "$DEST"
cd "$SRC"
git ls-files -z | grep -z -v -E '^(donnees|pilote|notes|presentation)/|^(CADRE|ATTENTE)\.md$|^revues/dossier_relecteur_exterieur/|^revues/(dossier_relecteur_2026-11-04|plan_2026-11-04|plan_2026-11-04_verification|note_terrain_2026-11|2026-11-17_audit_decisions_interets_revues)\.md$|^simulation/controle3/resultats[^/]*/|Plan de lancement article et Tenure|^\.claude/' \
  | xargs -0 tar -cf - | tar -xf - -C "$DEST"
mkdir -p "$DEST/experience"
cp -R experience/rejeu_final experience/exploratoire experience/exploratoire_2 experience/tirage experience/audit_sans_alerte experience/retraits_motif_a "$DEST/experience/"
rm -rf "$DEST/experience/audit_sans_alerte/fiches" "$DEST/experience/audit_sans_alerte/reponses"
cp experience/manifeste_verdicts.txt experience/gel_plan.json experience/journal_rejeu_final.jsonl experience/SHA256_sorties_finales.txt experience/rejeu_final_echec_1_SHA256.txt experience/NOTE_CORRECTIF_REJEU_FINAL.md "$DEST/experience/"
# personal paths in non-frozen texts only (frozen folders keep their bytes, see publication/ANCRES.md)
find "$DEST" -type f \( -name '*.md' -o -name '*.txt' -o -name '*.json' -o -name '*.jsonl' -o -name '*.csv' -o -name '*.log' -o -name '*.py' \) \
  ! -path "$DEST/banc/*" ! -path "$DEST/gel/*" ! -path "$DEST/simulation/*" ! -path "$DEST/REGLE.md" ! -path "$DEST/PLAN_EXPERIENCE.md" ! -path "$DEST/experience/*" ! -path "$DEST/depots/*_donnees/*" -print0 \
  | xargs -0 perl -pi -e 's#/Users/Otsoa/dev/autonomie-meritee#ROOT#g; s#/Users/Otsoa#HOME#g; s#-Users-Otsoa-dev-[\w-]*?-workspace#-HOME-workspace#g'
# further redactions (private names) are read from a local file kept outside the repository
R="$HOME/.config/autonomie-meritee/caviardage.pl"
[ -f "$R" ] || { echo "missing $R: refusing to build an unredacted snapshot"; rm -rf "$DEST"; exit 1; }
find "$DEST" -type f \( -name '*.md' -o -name '*.txt' -o -name '*.py' \) ! -path "$DEST/banc/*" ! -path "$DEST/gel/*" ! -path "$DEST/simulation/*" ! -path "$DEST/experience/*" ! -path "$DEST/REGLE.md" ! -path "$DEST/PLAN_EXPERIENCE.md" ! -path "$DEST/depots/*_donnees/*" -print0 | xargs -0 perl -pi -e "$(cat "$R")"
find "$DEST" -name '__pycache__' -type d -prune -exec rm -rf {} +
echo "snapshot in $DEST"
