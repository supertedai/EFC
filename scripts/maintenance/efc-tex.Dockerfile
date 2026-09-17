# efc-tex:2026 — EFC-papirers PDF-byggemiljø, reproduserbart fra repoet.
#
# Løser infra-blokk #2 (2026-09-17): pdflatex manglet på Hermes, og
# build-bridgen til .13 er stengt. Bygg skjer i denne containeren.
#
# Pakkesettet er MÅLT fra EFC-paperenes preambler (article, geometry,
# lmodern, amsmath/amssymb, booktabs, array, graphicx, xcolor, colortbl,
# hyperref + etoolbox/fancyhdr/titlesec/microtype/enumitem/stringenc/
# pdfescape som enkelte papere krever). Ny pakke som en paper trenger:
# legg til her, bygg på nytt, commit — slik holder bildet seg = repoet.
#
# Bygg:   docker build -t efc-tex:2026 -f scripts/maintenance/efc-tex.Dockerfile .
# Bruk:   scripts/maintenance/efc_pdf_bygg.sh <paper-mappe>
FROM texlive/texlive:latest-minimal

RUN tlmgr install latex latex-bin latex-fonts lm amsmath amsfonts geometry \
    booktabs tools graphics xcolor colortbl hyperref url \
    etoolbox fancyhdr titlesec microtype enumitem stringenc pdfescape

# latest-minimal har texlive-bin utenfor PATH; fiks slik at pdflatex finnes.
ENV PATH=/usr/local/texlive/2026/bin/x86_64-linux:${PATH}
