#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════
# efc_pdf_bygg.sh — EFC paper PDF build through docker (efc-tex:2026).
#
# Solves infra-block #2 (measured 2026-09-17): pdflatex was missing on
# Hermes, and the build bridge to .13 is closed. The build now happens in a
# locally versioned container (texlive minimal + the package set measured
# from the preprints), no bridge, no system TeX.
#
# Image recipe (if efc-tex:2026 has to be built on a new machine):
#   docker build -t efc-tex:2026 - <<'EOF'
#   FROM texlive/texlive:latest-minimal
#   RUN tlmgr install latex latex-bin latex-fonts lm amsmath amsfonts \
#       geometry booktabs tools graphics xcolor colortbl hyperref url \
#       etoolbox fancyhdr titlesec microtype enumitem stringenc pdfescape
#   ENV PATH=/usr/local/texlive/2026/bin/x86_64-linux:${PATH}
#   EOF
# (The package set is MEASURED from the EFC papers' preambles; if something
#  is missing, install it and commit: docker commit <container> efc-tex:2026.)
#
# Figshare writes are staged from the .12 guard (see efc-kunnskapslivssyklus
# §Publisering), NEVER from here — Hermes' datacenter IP is 403-blocked.
#
# Usage:   efc_pdf_bygg.sh <path-to-paper-directory>
# Effect:  builds <name>.tex → <name>.pdf in that directory; writes sha256 to
#          <directory>/.build.sha256 and returns it on stdout.
# Idempotence: always runs again; the output is deterministic given the .tex.
# ══════════════════════════════════════════════════════════════════════
set -euo pipefail

PAPER="${1:?usage: efc_pdf_bygg.sh <path-to-paper-directory>}"
[ -d "$PAPER" ] || { echo "efc_pdf_bygg: '$PAPER' is not a directory" >&2; exit 1; }

cd "$PAPER"
TEX=$(find . -maxdepth 1 -name '*.tex' | head -1)
[ -n "$TEX" ] || { echo "efc_pdf_bygg: no .tex in $PAPER" >&2; exit 1; }

if ! sudo -n docker image inspect efc-tex:2026 >/dev/null 2>&1; then
  echo "efc_pdf_bygg: the image efc-tex:2026 is missing — build it with the recipe in the script header" >&2
  exit 1
fi

# Clear any helper files from earlier runs so that .build.sha256 is clean
rm -f .build.sha256

# Two passes: refs/cross-references are resolved in pass 2
sudo -n docker run --rm -v "$PWD":/work -w /work efc-tex:2026 \
  pdflatex -interaction=nonstopmode -halt-on-error "${TEX#./}" >/dev/null
sudo -n docker run --rm -v "$PWD":/work -w /work efc-tex:2026 \
  pdflatex -interaction=nonstopmode -halt-on-error "${TEX#./}" >/dev/null

PDF="${TEX%.tex}.pdf"
[ -f "$PDF" ] || { echo "efc_pdf_bygg: no PDF produced" >&2; exit 1; }

SHA=$(sha256sum "$PDF" | cut -d' ' -f1)
printf '%s\n' "$SHA" > .build.sha256
echo "$SHA"
