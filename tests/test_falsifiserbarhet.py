"""Which nodes CAN be felled — and which cannot, with a reason.

Measured 2026-09-17: 0 of 74 public nodes carried a falsifier. But «0 of
74» measured the wrong thing. 47 of the 74 are not EFC claims at all:

    h2o, lys, optikk, regnbue, kjemi   established physics — not ours
    obs.*                              observations
    homo.*                             established biology
    verden.*, kosmos.jord.vulkan       instruments — they MEASURE

An instrument node has no falsifier because it claims nothing.
It measures. It can be miscalibrated, but that is another error.

The classes below have since 2026-09-18 been written into the nodes themselves,
as `stipulasjoner.ikke_falsifiserbar_grunn` — the same place as `buss_status`
and `motor_status` (card t_c11ffa45). This file says which prefixes are not
our claims; it does not measure that anyone has answered. The coverage
(113 of 113) is measured in `test_atlas_falsifiserbarhet_dekning.py`, and that
the reason is the node's OWN is measured in `test_atlas_avgjorelse.py`.

The 27 `efc.*` nodes are the ones that claim something EFC-specific. All 27
carry `sannhetsstatus: hypotese` — and a hypothesis without a falsifier has not
said what it excludes. This file holds the distinction. Without it, «can be
felled» and «is ours» melt into one number, and that number lies.
"""
from __future__ import annotations

import json
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
NODER = ROT / "schema" / "regime_nodes.jsonld"

#: Prefixes that are NOT EFC claims, each with its reason. A prefix that is
#: not listed here means a new kind of node nobody has assessed.
IKKE_EFC_PAASTAND = {
    "h2o": "established physics (IAPWS-95) — not our claim",
    "lys": "observation",
    "optikk": "established physics (NIST)",
    "regnbue": "established physics",
    "kjemi": "established structure (IUPAC)",
    "obs": "observation — not a model claim",
    "homo": "established biology",
    "verden": "instrument — measures, does not claim",
    "kosmos": "instrument — measures, does not claim",
}


def _offentlige():
    return [n for n in json.loads(NODER.read_text(encoding="utf-8"))["nodes"]
            if n.get("synlighet") == "offentlig"]


class TestFalsifiserbarhet:

    def test_hver_efc_paastand_kan_felles(self):
        """Every EFC node that CLAIMS something shall be felleable.

        A node can escape for two reasons, and ONLY two: it is a stub
        (compute() raises NotImplementedError), or it is a published framework
        whose threshold is not fixed. Both shall say so themselves, and both
        are pinned in the count. A third reason shall fell this test — that is
        how a new excuse becomes visible.
        """
        mangler = [n["id"] for n in _offentlige()
                   if n["id"].startswith("efc.")
                   and "ville_falsifisere" not in n
                   and (n.get("falsifiserbarhet") or {}).get("status")
                   not in ("stub", "terskel_ikke_fastsatt")]
        assert mangler == [], f"EFC claims without a falsifier: {mangler}"

    def test_falsifikatoren_sier_mer_enn_paastanden(self):
        """«It would fail if it is wrong» is not a falsifier.

        The four that existed before this test ALL had identical text:
        «the self-application would fail if the atlas could not be described
        by its own schema». That is a claim about the ATLAS, not about the
        node — and it was copied onto four nodes. A falsifier must be the
        node's OWN.
        """
        tekster = [n["ville_falsifisere"] for n in _offentlige()
                   if "ville_falsifisere" in n]
        duplikater = {t for t in tekster if tekster.count(t) > 1}
        assert duplikater == set(), (
            f"identical falsifier on several nodes: {duplikater}")

    def test_falsifikatoren_er_lang_nok_til_aa_bety_noe(self):
        korte = [n["id"] for n in _offentlige() if "ville_falsifisere" in n
                 and len(n["ville_falsifisere"]) < 40]
        assert korte == [], f"too short falsifiers: {korte}"

    def test_de_ikke_efc_nodene_er_kjent_klassifisert(self):
        """The ones without a falsifier shall fall in a KNOWN category."""
        ukjente = {n["id"].split(".")[0] for n in _offentlige()
                   if not n["id"].startswith("efc.")
                   and "ville_falsifisere" not in n}
        ukjente -= set(IKKE_EFC_PAASTAND)
        assert ukjente == set(), (
            f"new prefixes without an assessment: {sorted(ukjente)}")

    def test_en_stub_kan_ikke_felles_og_skal_ikke_telle(self):
        """Review 2026-09-17: a STUB had `ville_falsifisere` set to
        «cannot be falsified because it computes nothing». It is honest, but
        it is a DESCRIPTION OF A STATE — not a falsifier — and it made the
        number go up while the field answered something else.

        A node whose engine raises NotImplementedError shall not have a
        falsifier. It shall have a reason.

        Measured 2026-09-20 (card t_2d7a6537, review round 1): the two
        stubs (lensing, cluster) were reclassified to `terskel_ikke_fastsatt`
        — the card's own word for «the threshold cannot be fixed honestly».
        So no public node is a `stub` anymore; a new stub is a decision.
        """
        stubber = [n for n in _offentlige()
                   if (n.get("falsifiserbarhet") or {}).get("status") == "stub"]
        assert len(stubber) == 0, f"expected 0 stubs, got {len(stubber)}"
        for n in stubber:
            assert "ville_falsifisere" not in n, (
                f"{n['id']} is a stub BUT has a falsifier — then a description "
                f"of a state counts as satisfied falsifiability")

    def test_en_terskel_som_ikke_er_fastsatt_er_ikke_et_kriterium(self):
        """Review 2026-09-17, round 2: the five framework nodes used
        formulations such as «stated threshold» and «more than the stated
        uncertainty» WITHOUT giving the value.

        It is the third time for the same shortcoming: the field was filled
        in, and answered a different question than its own. For the four
        `efc.selv.*` it was a copy. For «0 of 74» it was the wrong denominator.
        For the stubs it was a description of a state. Here it is an INTENTION.

        A node that cannot state a threshold cannot be felled. It shall say
        so — not write the word «threshold» and let it pass.
        """
        # SAME population as : EFC claims. Otherwise the two
        # sides count different sets and the sum cannot be right.
        avventer = [n for n in _offentlige()
                    if (n.get("falsifiserbarhet") or {}).get("status")
                    in ("terskel_ikke_fastsatt", "stub")]
        # Measured 2026-09-20 (card t_2d7a6537): the two engines that carried
        # `terskel_ikke_fastsatt` in a fragment now carry the contract their
        # thresholds stand in (BIG-SPARC/DH_over_rd), so they left this set.
        # The two that compute nothing (lensing, cluster) stay — now as
        # `terskel_ikke_fastsatt` (the card's word for the honest position),
        # and they still shall not count as satisfied falsifiability.
        assert len(avventer) == 2, f"expected 2 without a fixed threshold, got {len(avventer)}"
        for n in avventer:
            assert "ville_falsifisere" not in n, (
                f"{n['id']} lacks a threshold BUT has a falsifier")
            assert "NOT fixed" in n["falsifiserbarhet"]["grunn"], (
                f"{n['id']} does not say itself what is missing")

    def test_tallet_er_kjent(self):
        """The number shall be known, not merely surprising.

        If it went down, an EFC node lost its falsifier. If it went up, a node
        has been reclassified — and then someone shall have decided it.
        """
        off = _offentlige()
        kan = sum(1 for n in off if "ville_falsifisere" in n)
        avventer = sum(1 for n in off
                       if (n.get("falsifiserbarhet") or {}).get("status")
                       in ("stub", "terskel_ikke_fastsatt"))
        assert len(off) == 116, f"the public set changed: {len(off)}"
        assert kan == 29, (
            f"can be felled: {kan} — expected 29. 19 was wrong: 2 stubs and 6 "
            f"framework nodes without a fixed threshold could not be felled; "
            f"27 became 29 when two engines got the contract their threshold "
            f"stands in (2026-09-20, card t_2d7a6537)")
        assert avventer == 2, (
            f"waiting: {avventer} — expected 2 (the two that compute "
            f"nothing: lensing and cluster, now `terskel_ikke_fastsatt`). "
            f"Was 4 while the two engines carried `terskel_ikke_fastsatt` "
            f"in a fragment; the two categories stay disjoint.")
        assert kan + avventer == 31, (
            f"{kan} + {avventer} = {kan + avventer}, but there are 31 EFC "
            f"nodes among the public ones")
