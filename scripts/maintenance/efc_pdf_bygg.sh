#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════
# efc_pdf_bygg.sh — EFC-paper PDF-bygg gjennom docker (efc-tex:2026).
#
# Løser infra-blokk #2 (målt 2026-09-17): pdflatex manglet på Hermes,
# og build-bridgen til .13 er stengt. Bygg skjer nå i en lokalt versjonert
# container (texlive minimal + preprintenes målte pakkesett), ingen bro,
# ingen system-TeX.
#
# Bildeoppskrift (om efc-tex:2026 må bygges på ny maskin):
#   docker build -t efc-tex:2026 - <<'EOF'
#   FROM texlive/texlive:latest-minimal
#   RUN tlmgr install latex latex-bin latex-fonts lm amsmath amsfonts \
#       geometry booktabs tools graphics xcolor colortbl hyperref url \
#       etoolbox fancyhdr titlesec microtype enumitem stringenc pdfescape
#   ENV PATH=/usr/local/texlive/2026/bin/x86_64-linux:${PATH}
#   EOF
# (Pakkesettet er målt fra EFC-paperenes preambler; mangler noe, installér
#  og commit: docker commit <container> efc-tex:2026.)
#
# Figshare-skrivingen gås av sted fra .12-vakten (se efc-kunnskapslivssyklus
# §Publisering), ALDRI herfra — Hermes' datasenter-IP er 403-blokkert.
#
# Bruk:   efc_pdf_bygg.sh <sti-til-paper-mappe>
# Effekt: bygger <navn>.tex → <navn>.pdf i mappen; skriver sha256 til
#         <mappe>/.build.sha256 og returnerer den på stdout.
# Idempotens: kjører alltid på nytt; output er deterministisk gitt .tex.
# ══════════════════════════════════════════════════════════════════════
set -euo pipefail

PAPER="${1:?bruk: efc_pdf_bygg.sh <sti-til-paper-mappe>}"
[ -d "$PAPER" ] || { echo "efc_pdf_bygg: '$PAPER' er ikke en mappe" >&2; exit 1; }

cd "$PAPER"
TEX=$(find . -maxdepth 1 -name '*.tex' | head -1)
[ -n "$TEX" ] || { echo "efc_pdf_bygg: ingen .tex i $PAPER" >&2; exit 1; }

if ! sudo -n docker image inspect efc-tex:2026 >/dev/null 2>&1; then
  echo "efc_pdf_bygg: bildet efc-tex:2026 mangler — bygg det med oppskriften i script-hodet" >&2
  exit 1
fi

# Rens evt. hjelpefiler fra tidligere kjøringer slik at .build.sha256 er ren
rm -f .build.sha256

# To pass: refs/kryssreferanser settes i pass 2
sudo -n docker run --rm -v "$PWD":/work -w /work efc-tex:2026 \
  pdflatex -interaction=nonstopmode -halt-on-error "${TEX#./}" >/dev/null
sudo -n docker run --rm -v "$PWD":/work -w /work efc-tex:2026 \
  pdflatex -interaction=nonstopmode -halt-on-error "${TEX#./}" >/dev/null

PDF="${TEX%.tex}.pdf"
[ -f "$PDF" ] || { echo "efc_pdf_bygg: ingen PDF produsert" >&2; exit 1; }

SHA=$(sha256sum "$PDF" | cut -d' ' -f1)
printf '%s\n' "$SHA" > .build.sha256
echo "$SHA"
