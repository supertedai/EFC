# efc-tex:2026 — PDF build environment for EFC papers, reproducible from the repo.
#
# Solves infra-block #2 (2026-09-17): pdflatex was missing on Hermes, and the
# build bridge to .13 is closed. The build happens in this container.
#
# The package set is MEASURED from the EFC papers' preambles (article, geometry,
# lmodern, amsmath/amssymb, booktabs, array, graphicx, xcolor, colortbl,
# hyperref + etoolbox/fancyhdr/titlesec/microtype/enumitem/stringenc/
# pdfescape, which some papers require). A new package a paper needs:
# add it here, rebuild, commit — that is how the image stays equal to the repo.
#
# Build:  docker build -t efc-tex:2026 -f scripts/maintenance/efc-tex.Dockerfile .
# Usage:  scripts/maintenance/efc_pdf_bygg.sh <paper-directory>
FROM texlive/texlive:latest-minimal

RUN tlmgr install latex latex-bin latex-fonts lm amsmath amsfonts geometry \
    booktabs tools graphics xcolor colortbl hyperref url \
    etoolbox fancyhdr titlesec microtype enumitem stringenc pdfescape

# latest-minimal has texlive-bin outside PATH; fix it so pdflatex is found.
ENV PATH=/usr/local/texlive/2026/bin/x86_64-linux:${PATH}
