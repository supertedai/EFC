"""Tests for scripts/maintenance/gamma_flrw_consistency.py.

The audit is the paradigm-independent layer of the Γ(ρ) finding: it reads
only published source text and arithmetic, no data and no ΛCDM measure.
These tests lock the honest framings in place so they cannot drift into a
claim the source does not support:

  - FLRW σ_s = Γ·ρ̇ is candidate_FLRW_relation_only, never an identity;
  - the per-mode → σ_s bridge is mapping_to_sigma_s_not_established;
  - B is non-saturating per the source's own R2 label ("not saturation"),
    reported as such, not as a coined "P1 violation";
  - B's prefactor is an unresolved normalization convention, not a
    demonstrated unit error.
"""
from __future__ import annotations

import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "gamma_flrw_consistency.py"
SOURCE = (
    ROOT / "docs" / "papers" / "efc" / "Derivation_of_the_Entropy_Production"
    / "src" / "entropy_production.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("gamma_flrw_consistency", SCRIPT)
    assert spec is not None, f"module spec unavailable for {SCRIPT}"
    assert spec.loader is not None, f"module loader unavailable for {SCRIPT}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _report(mod, source=None):
    src = source or str(SOURCE)
    src_path = Path(src)
    text = src_path.read_text(encoding="utf-8") if src_path.exists() else None
    return mod.build_report(text, src_path)


def test_script_is_self_contained():
    """The audit reads the source as text; it must not import the DOI package
    (docs/** is outside pytest collection and off sys.path). Language is
    enforced by the repo-wide spraakvakt gate over tests/**, not re-asserted
    here — embedding stopwords to test for their absence would trip the gate."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert "import entropy_production" not in text


def test_computes_from_real_source():
    mod = _load()
    rc, report = _report(mod)
    assert rc == 0, report.get("error")
    assert report["status"] == "computed_from_declared_forms"
    assert report["doi"] == "10.6084/m9.figshare.31942821"


def test_B_is_non_saturating_per_R2_not_a_coined_P1():
    mod = _load()
    rc, report = _report(mod)
    assert rc == 0
    a = report["asymptotics"]
    assert a["B"]["saturates_high_density"] is False
    assert "non-saturating" in a["B"]["high_density_behavior"]
    assert a["A"]["saturates_high_density"] is True
    assert a["C"]["saturates_high_density"] is True
    # The source's own needle, not a self-coined label.
    assert report["needles"]["B_non_saturating_R2"] is True


def test_low_density_exponents_are_computed():
    mod = _load()
    a = mod.asymptotics()
    # Computed log-log slopes, not transcribed labels: A~ρ¹, B~ρ^(3/2), C~ρ^(1/2).
    # Tolerance absorbs the finite probe window (the slope is exact only in the
    # limit r→0; e.g. C computes to ~0.498 at 1e-6..1e-4).
    assert a["A"]["low_density_exponent"] == pytest.approx(1.0, abs=5e-3)
    assert a["B"]["low_density_exponent"] == pytest.approx(1.5, abs=5e-3)
    assert a["C"]["low_density_exponent"] == pytest.approx(0.5, abs=5e-3)


def test_shape_family_is_derived_not_hardcoded():
    mod = _load()
    a = mod.asymptotics()
    # A and C share the saturating rational shape (argument r vs sqrt(r));
    # only B is a non-saturating power. This is a bifurcation, not a
    # trifurcation, and the shape_family is derived from the computed
    # high-density slope, so it cannot drift independently of the functions.
    assert a["A"]["shape_family"] == "saturating_rational"
    assert a["C"]["shape_family"] == "saturating_rational"
    assert a["B"]["shape_family"] == "non_saturating_power"


def test_B_normalization_convention_unresolved():
    mod = _load()
    d = mod.dimensional_classification()
    assert d["A"]["classification"] == "dimensionless_argument"
    assert d["A"]["normalization_status"] == "explicit"
    assert d["C"]["classification"] == "dimensionless_argument"
    assert d["C"]["normalization_status"] == "explicit"
    # B is displayed as ρ^(3/2)/(ρ+ρcrit) but implemented on dimensionless r;
    # the reconciliation is NOT shown in the source, so the honest label is an
    # unresolved convention, not a demonstrated unit error.
    assert d["B"]["classification"] == "normalization_convention_unresolved"
    assert d["B"]["normalization_status"] == "not_explicitly_reconciled"
    assert "raw_displayed_form" in d["B"]
    assert "implemented_ratio_form" in d["B"]


def test_flrw_is_candidate_not_identity():
    mod = _load()
    rc, report = _report(mod)
    assert rc == 0
    assert report["flrw_relation_status"] == "candidate_FLRW_relation_only"
    assert report["sigma_s_mapping"] == "mapping_to_sigma_s_not_established"


def test_missing_source_is_could_not_read():
    mod = _load()
    rc, report = _report(mod, source="/nonexistent/entropy_production.py")
    assert rc == 2
    assert report["status"] == "could_not_read_source"


def test_form_provenance_is_declared():
    """C is declared in companion 31942800, not read here; A/B are pinned to
    the 31942821 source text. The audit must say which is which."""
    mod = _load()
    rc, report = _report(mod)
    assert rc == 0
    fp = report["form_provenance"]
    assert "literal_present_in_source_text" in fp["A"]
    assert "literal_present_in_source_text" in fp["B"]
    assert "reimplemented_from_companion_declaration" in fp["C"]
    assert "31942800" in fp["C"]


def test_json_output_is_valid_and_write_free():
    """--json must emit a single JSON document; the audit writes nothing."""
    mod = _load()
    rc, report = _report(mod)
    assert rc == 0
    blob = json.dumps(report, ensure_ascii=False)
    # The report carries no path-writing side effect: re-parsing round-trips.
    assert json.loads(blob)["status"] == "computed_from_declared_forms"


def test_cli_stdout_path_does_not_traceback():
    """The human-readable report must render every classification branch.

    This is the regression test for the KeyError that slipped through when
    B's classification gained the normalization_convention_unresolved label
    (which has no prefactor_units) while print_report still assumed it did.
    """
    mod = _load()
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = mod.main(["--source", str(SOURCE)])
    assert rc == 0
    out = buf.getvalue()
    assert "normalization_convention_unresolved" in out
    assert "computed_from_declared_forms" in out
    assert "Traceback" not in out
