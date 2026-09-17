#!/usr/bin/env python3
"""efc_change_id.py — change_id-kontrakten og projeksjonen av aktivitetsloggen.

KANONISK KILDE: ``logs/activity.jsonl`` — append-only, ett JSON-objekt per linje.
Changelogen er ikke en kilde; den er en projeksjon av denne loggen.

change_id
---------
Hver hendelse har en stabil ``change_id`` på formen ``CHG-<12 heksadesimale>``.
Den er sha256 over hendelsens kanoniske innhold UTEN ``change_id``-feltet selv —
én regel for alle hendelsestyper, slik at

  * samme hendelse alltid gir samme id (rebygging er idempotent),
  * enhver endring av en logglinje endrer id-en (og avsløres av sjekken),
  * id-en kan etterregnes av hvem som helst, fra loggen alene.

Linjer skrevet før kontrakten mangler feltet. De får sin ``change_id``
AVLEDET med samme regel, og sjekken rapporterer dem som ``legacy`` — aldri som
en hard feil. Avledningen er total: ingen linje faller utenfor projeksjonen.

Projeksjonen
------------
``docs/validation-ledger/data/changelog.json`` (nøkkelen ``activity_projection``)
og den markerte regionen i ``docs/public/EFC_Changelog.html`` er DETERMINISTISKE
funksjoner av loggen og generatorversjonen. ``input_hash`` = sha256 av den
kanoniske projeksjons-inputen: alle hendelser UNNTATT metatypen
``projection_built``.

Hvorfor metatypen er unntatt: projeksjonen loggfører sin egen proveniens
(generator + versjon + input_hash) som en ``projection_built``-hendelse i
loggen. Tok projeksjonen med sin egen provenienshendelse i inputen, ville hver
rebygging endret inputen og dermed sin egen output — den ville aldri
konvergere. Unntaket gjør rebygging idempotent: samme endringssett gir
bit-identisk output, uansett hvor mange ganger den bygges.

Manuell redigering av regionen (eller av projeksjonsblokken i JSON-en) gir
avvik mot den regenererte projeksjonen og avvises av
``efc_changelog_check.py``, som CI kjører.

Ingen skriving skjer her. Denne modulen er ren logikk; generatoren
(``efc_auto_changelog.py``) skriver, sjekken leser.
"""
from __future__ import annotations

import hashlib
import json
import re
from html import escape
from pathlib import Path

GENERATOR = "efc_auto_changelog.py"
GENERATORVERSJON = "2.0"

CHANGE_ID_RE = re.compile(r"^CHG-[0-9a-f]{12}$")
EVENT_ID_RE = re.compile(r"^EVT-(\d{4})-(\d{6})$")

PROJ_NOKKEL = "activity_projection"
META_AKSJON = "projection_built"
KILDELOGG = "logs/activity.jsonl"

HTML_START = "<!-- efc-changelog-projeksjon:start -->"
HTML_SLUTT = "<!-- efc-changelog-projeksjon:slutt -->"

# Projeksjonens egne utdata (og kildeloggen) er ikke «endringer» som skal
# registreres på nytt: de ER loggen og dens speil. Uten dette unntaket ville
# hver projeksjon registrert seg selv og aldri konvergert.
IGNORERTE_STIER = (
    KILDELOGG,
    "docs/validation-ledger/data/changelog.json",
    "docs/public/EFC_Changelog.html",
)


class KontraktFeil(RuntimeError):
    """Brudd på change_id-/projeksjonskontrakten."""


def kanonisk(obj) -> str:
    """Kanonisk JSON: sorterte nøkler, ingen overflødig luft."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def beregn_change_id(hendelse: dict) -> str:
    """change_id = sha256 over hendelsens innhold, uten change_id selv."""
    grunnlag = {k: v for k, v in hendelse.items() if k != "change_id"}
    return "CHG-" + hashlib.sha256(kanonisk(grunnlag).encode("utf-8")).hexdigest()[:12]


def change_id_for(hendelse: dict) -> str:
    """Lagret change_id om den finnes, ellers avledet (legacy-linjer)."""
    lagret = hendelse.get("change_id")
    return str(lagret) if lagret else beregn_change_id(hendelse)


def les_logg(sti) -> tuple[list[dict], list[dict]]:
    """Les aktivitetsloggen. Returnerer (hendelser, feil)."""
    sti = Path(sti)
    hendelser: list[dict] = []
    feil: list[dict] = []
    if not sti.is_file():
        return [], [{"type": "logg_mangler", "fil": str(sti)}]
    for nr, linje in enumerate(sti.read_text(encoding="utf-8").splitlines(), 1):
        if not linje.strip():
            continue
        try:
            hendelse = json.loads(linje)
        except json.JSONDecodeError as ex:
            feil.append({"type": "ugyldig_json", "linje": nr, "msg": str(ex)[:120]})
            continue
        if not isinstance(hendelse, dict):
            feil.append({"type": "ikke_objekt", "linje": nr})
            continue
        hendelser.append(hendelse)
    return hendelser, feil


def id_kontroll(hendelser: list[dict]) -> list[dict]:
    """Hver linjes change_id: gyldig form, lik sitt eget innhold, unik."""
    feil: list[dict] = []
    sett: dict[str, int] = {}
    for nr, hendelse in enumerate(hendelser, 1):
        lagret = hendelse.get("change_id")
        if lagret is not None:
            if not CHANGE_ID_RE.match(str(lagret)):
                feil.append({"type": "ugyldig_change_id", "linje": nr,
                             "change_id": lagret})
            elif str(lagret) != beregn_change_id(hendelse):
                feil.append({"type": "change_id_avviker_fra_innhold", "linje": nr,
                             "change_id": lagret,
                             "forventet": beregn_change_id(hendelse)})
        cid = change_id_for(hendelse)
        if cid in sett:
            feil.append({"type": "change_id_kollisjon", "change_id": cid,
                         "linjer": [sett[cid], nr]})
        sett.setdefault(cid, nr)
    return feil


def projeksjonsinput(hendelser: list[dict]) -> tuple[list[dict], dict]:
    """Projeksjonens input: endringene, sortert nyeste først.

    Metatypen ``projection_built`` holdes utenfor (se moduldocstringen).
    Returnerer (oppføringer, statistikk).
    """
    oppføringer: list[dict] = []
    statistikk = {"meta_hendelser": 0, "legacy_uten_change_id": 0}
    for hendelse in hendelser:
        if hendelse.get("action") == META_AKSJON:
            statistikk["meta_hendelser"] += 1
            continue
        if not hendelse.get("change_id"):
            statistikk["legacy_uten_change_id"] += 1
        occurred = str(hendelse.get("occurred_at") or "")
        oppføringer.append({
            "change_id": change_id_for(hendelse),
            "event_id": hendelse.get("event_id"),
            "occurred_at": hendelse.get("occurred_at"),
            "date": occurred[:10],
            "action": hendelse.get("action"),
            "role": hendelse.get("role"),
            "kanban_card": hendelse.get("kanban_card"),
            "files": list(hendelse.get("files") or []),
            "why": hendelse.get("why"),
            "result": hendelse.get("result"),
            "reversible": hendelse.get("reversible"),
        })
    oppføringer.sort(key=lambda o: (str(o["occurred_at"]), o["change_id"]),
                     reverse=True)
    return oppføringer, statistikk


def input_hash(oppføringer: list[dict]) -> str:
    return hashlib.sha256(kanonisk(oppføringer).encode("utf-8")).hexdigest()


def projeksjonsblokk(oppføringer: list[dict]) -> dict:
    return {
        "generator": GENERATOR,
        "generator_version": GENERATORVERSJON,
        "source": KILDELOGG,
        "input_hash": input_hash(oppføringer),
        "count": len(oppføringer),
        "entries": oppføringer,
    }


def json_projeksjon(eksisterende: dict, oppføringer: list[dict]) -> dict:
    """Ny changelog.json: alt annet bevares, projeksjonsblokken erstattes."""
    data = dict(eksisterende)
    data[PROJ_NOKKEL] = projeksjonsblokk(oppføringer)
    return data


def json_tekst(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _html_li(oppføring: dict) -> str:
    cid = escape(str(oppføring["change_id"]), quote=True)
    filer = ", ".join(f"<code>{escape(str(f), quote=True)}</code>"
                      for f in (oppføring["files"] or []))
    detalj = f" {filer} &mdash;" if filer else ""
    return (
        f'  <li data-change-id="{cid}">'
        f'<strong>{escape(str(oppføring["date"]), quote=True)}</strong>'
        f' &mdash; <code>{escape(str(oppføring["action"]), quote=True)}</code>'
        f' &middot; <em>{escape(str(oppføring["role"]), quote=True)}</em>'
        f' &middot; kort <code>{escape(str(oppføring["kanban_card"]), quote=True)}</code>:'
        f'{detalj} {escape(str(oppføring["why"]), quote=True)}'
        f' &mdash; <span class="efc-change-id">{cid}</span></li>'
    )


def html_region(oppføringer: list[dict]) -> str:
    """Den genererte regionen i EFC_Changelog.html — bit-identisk per input."""
    ih = input_hash(oppføringer)
    hode = (
        f"{HTML_START}\n"
        f"<!-- GENERERT — ikke rediger manuelt. Kilde: {KILDELOGG} · "
        f"generator: {GENERATOR} v{GENERATORVERSJON} · input_hash: {ih} · "
        f"{len(oppføringer)} endring(er) · "
        f"regenerer: python3 scripts/maintenance/{GENERATOR} -->"
    )
    kropp = "\n".join(_html_li(o) for o in oppføringer)
    return f"{hode}\n{kropp}\n{HTML_SLUTT}"


def sett_inn_region(html: str, region: str, aar: str) -> str:
    """Skriv regionen inn i siden — idempotent, alltid samme resultat."""
    if HTML_START in html and HTML_SLUTT in html:
        start = html.index(HTML_START)
        slutt = html.index(HTML_SLUTT, start) + len(HTML_SLUTT)
        return html[:start] + region + html[slutt:]
    anker = f"<h2>{aar}</h2>"
    hode_idx = html.find(anker)
    if hode_idx < 0:
        raise KontraktFeil(f"fant ikke årsanker {anker!r} i changelog-siden")
    ul_idx = html.find("<ul>", hode_idx)
    if ul_idx < 0:
        raise KontraktFeil("fant ikke <ul> etter årsankeret i changelog-siden")
    inn = ul_idx + len("<ul>")
    return html[:inn] + "\n" + region + html[inn:]


def region_fra_html(html: str) -> str | None:
    if HTML_START not in html or HTML_SLUTT not in html:
        return None
    start = html.index(HTML_START)
    slutt = html.index(HTML_SLUTT, start) + len(HTML_SLUTT)
    return html[start:slutt]


def _region_ider(region: str) -> list[str | None]:
    return re.findall(r'<li[^>]*data-change-id="([^"]*)"', region)


def _region_antall_li(region: str) -> int:
    return region.count("<li")


def avvik(logg_sti, json_sti, html_sti) -> dict:
    """Sjekk hele kjeden: registerpost → changelog.json → EFC_Changelog.html.

    Returnerer {"feil": [...], "info": {...}}. Harde feil = projeksjonen er
    ikke en tro projeksjon av loggen, eller de tre flatene peker ikke på
    samme change_id.
    """
    feil: list[dict] = []
    hendelser, lesefeil = les_logg(logg_sti)
    feil += lesefeil
    feil += id_kontroll(hendelser)
    oppføringer, statistikk = projeksjonsinput(hendelser)
    ih = input_hash(oppføringer)
    fasit = {o["change_id"] for o in oppføringer}
    info = dict(statistikk)
    info.update({"endringer": len(oppføringer), "input_hash": ih,
                 "generator": GENERATOR, "generator_version": GENERATORVERSJON})

    # changelog.json
    json_sti = Path(json_sti)
    data: dict = {}
    if not json_sti.is_file():
        feil.append({"type": "changelog_json_mangler", "fil": str(json_sti)})
    else:
        try:
            data = json.loads(json_sti.read_text(encoding="utf-8"))
        except json.JSONDecodeError as ex:
            feil.append({"type": "changelog_json_ugyldig", "msg": str(ex)[:120]})
            data = {}
    blokk = data.get(PROJ_NOKKEL) if isinstance(data, dict) else None
    json_ider: list[str] = []
    if not isinstance(blokk, dict):
        if json_sti.is_file():
            feil.append({"type": "projeksjonsblokk_mangler",
                         "nokkel": PROJ_NOKKEL})
    else:
        if blokk.get("generator") != GENERATOR:
            feil.append({"type": "json_generator_avviker",
                         "funnet": blokk.get("generator"), "fasit": GENERATOR})
        if blokk.get("generator_version") != GENERATORVERSJON:
            feil.append({"type": "json_generatorversjon_avviker",
                         "funnet": blokk.get("generator_version"),
                         "fasit": GENERATORVERSJON})
        if blokk.get("input_hash") != ih:
            feil.append({"type": "json_input_hash_avviker",
                         "funnet": blokk.get("input_hash"), "fasit": ih})
        poster = blokk.get("entries")
        if not isinstance(poster, list):
            feil.append({"type": "json_poster_ugyldig"})
            poster = []
        if poster != oppføringer:
            feil.append({"type": "json_projeksjon_avviker",
                         "antall_fasit": len(oppføringer),
                         "antall_funnet": len(poster)})
        for nr, post in enumerate(poster, 1):
            if not isinstance(post, dict):
                feil.append({"type": "json_post_ugyldig", "nr": nr})
                continue
            cid = post.get("change_id")
            if not cid or not CHANGE_ID_RE.match(str(cid)):
                feil.append({"type": "json_post_uten_change_id",
                             "nr": nr, "event_id": post.get("event_id")})
            else:
                json_ider.append(str(cid))
    for cid in sorted(fasit - set(json_ider)):
        feil.append({"type": "mangler_json_post", "change_id": cid})
    for cid in sorted(set(json_ider) - fasit):
        feil.append({"type": "ukjent_change_id_i_json", "change_id": cid})

    # EFC_Changelog.html
    html_sti = Path(html_sti)
    if not html_sti.is_file():
        feil.append({"type": "changelog_side_mangler", "fil": str(html_sti)})
    else:
        html = html_sti.read_text(encoding="utf-8")
        region = region_fra_html(html)
        if region is None:
            feil.append({"type": "html_region_mangler"})
        else:
            fasit_region = html_region(oppføringer)
            if region != fasit_region:
                feil.append({"type": "html_region_avviker",
                             "melding": "manuell redigering eller utdatert "
                                        "projeksjon — regenerer siden"})
            ider = _region_ider(region)
            antall_li = _region_antall_li(region)
            for cid in ider:
                if not cid or not CHANGE_ID_RE.match(cid):
                    feil.append({"type": "html_linje_uten_change_id",
                                 "change_id": cid or ""})
            if antall_li != len(ider):
                feil.append({"type": "html_linje_uten_change_id",
                             "antall_li": antall_li, "antall_med_id": len(ider)})
            rene_ider = {c for c in ider if c}
            for cid in sorted(fasit - rene_ider):
                feil.append({"type": "mangler_html_linje", "change_id": cid})
            for cid in sorted(rene_ider - fasit):
                feil.append({"type": "ukjent_change_id_i_html", "change_id": cid})
            # Utenfor regionen: den håndvedlikeholdte historikken er grandfathered
            # (INFO — hull skal være synlige, ikke skjulte), men en change_id der
            # ville være en fabrikkert korrelasjonsnøkkel og er en hard feil.
            utenfor = html.replace(region, "")
            for cid in re.findall(r'data-change-id="([^"]*)"', utenfor) + \
                    re.findall(r'class="efc-change-id">([^<]*)<', utenfor):
                feil.append({"type": "change_id_utenfor_projeksjonen",
                             "change_id": cid})
            info["historiske_linjer_utenfor_regionen"] = utenfor.count("<li")

    # Projeksjonens proveniens skal stå i loggen (generatorversjon + input-hash)
    if not any(
        h.get("action") == META_AKSJON
        and h.get("generator") == GENERATOR
        and h.get("generator_version") == GENERATORVERSJON
        and h.get("input_hash") == ih
        for h in hendelser
    ):
        feil.append({"type": "projeksjon_ikke_logget",
                     "generator": GENERATOR, "generator_version": GENERATORVERSJON,
                     "input_hash": ih})
    info["legacy_rapportert"] = bool(statistikk["legacy_uten_change_id"])
    return {"feil": feil, "info": info}
