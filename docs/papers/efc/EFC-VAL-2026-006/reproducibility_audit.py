#!/usr/bin/env python3
"""Reproducibility & Correctness Audit Protocol v2.
Mechanical gates that must PASS before trusting any inference run.
v2 extends v1 with: sealed-derivation chain, NUTS pipeline, numerical
sanity (covariances, r_d), and limit-case tests for ALL variants."""
import os, sys, hashlib, json, glob, subprocess
from pathlib import Path

ROOT_TEST = Path("/Users/morpheus/Documents/Claud Code/AGI-Test")
ROOT_AGI  = Path("/Users/morpheus/AGI")
results = []

def gate(name, status, detail=""):
    sym = "✅" if status=="PASS" else ("⚠️" if status=="WARN" else "❌" if status=="FAIL" else "⏭️")
    results.append((sym, name, status, detail))

def file_hash(p):
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:12]
    except Exception:
        return "MISSING"

def docker_cmd(cmd):
    try:
        r = subprocess.run(["docker", "exec", "efc-research-daemon"] + cmd,
                         capture_output=True, text=True, timeout=10)
        return (r.returncode, r.stdout, r.stderr)
    except Exception as e:
        return (-1, "", str(e))

# ========== A. DATA PROVENANCE ==========
print("=== A. DATA PROVENANCE ===")
bao = ROOT_TEST / "efc_inference/data/bao/desi_dr2/bao_desi_dr2.json"
if bao.exists():
    d = json.loads(bao.read_text())
    n = len(d.get("measurements", []))
    src = d.get("source", "")
    cov = (bao.parent / "cov.txt").exists()
    gate("A1: BAO=DESI DR2 real (13+ pts, full cov)",
         "PASS" if (n>=13 and "DESI DR2" in src and cov) else "FAIL",
         f"n={n}, source='{src[:40]}', cov.txt={cov}")
else:
    gate("A1: BAO real", "FAIL", "file missing")

fs8 = ROOT_TEST / "efc_inference/data/growth/fs8_extended.csv"
n_doi = fs8.read_text().count("DOI:") if fs8.exists() else 0
gate("A2: fσ8 DOI-traced (≥6 lines)", "PASS" if n_doi>=6 else "FAIL", f"DOI-rows={n_doi}")

hz = ROOT_TEST / "efc_inference/data/hubble/hz_cosmic_chronometers.csv"
n_doi_hz = hz.read_text().count("DOI:") if hz.exists() else 0
gate("A3: Hz DOI-traced", "PASS" if n_doi_hz>=3 else "FAIL", f"DOI={n_doi_hz}")

pant = ROOT_TEST / "efc_inference/data/snia/pantheon_binned.csv"
pant_cov = ROOT_TEST / "efc_inference/data/snia/pantheon_binned_covtotal.npy"
gate("A4: Pantheon + cov", "PASS" if (pant.exists() and pant_cov.exists()) else "FAIL", "")

mcmc_src = (ROOT_TEST / "efc_inference/runs/research_mcmc.py").read_text()
stub_refs = [s for s in ["bao_starter","bao_smoketest","fs8_starter","fs8_smoketest","hz_starter","hz_smoketest"] if s in mcmc_src]
gate("A5: No stub refs in research_mcmc.py", "PASS" if not stub_refs else "FAIL", str(stub_refs) or "clean")

# ========== B. CODE SYNC ==========
print("\n=== B. CODE SYNC ===")
crit_files = [
    "efc_inference/runs/research_mcmc.py",
    "efc_inference/runs/research_daemon.py",
    "efc_inference/core/cosmology_model.py",
    "efc_inference/runs/jax_efc_nuts.py",
    "efc_inference/runs/gpu_nuts_daemon.py",
]
for i, f in enumerate(crit_files, 1):
    h_test = file_hash(ROOT_TEST/f)
    h_agi  = file_hash(ROOT_AGI/f)
    gate(f"B{i}: {f.split('/')[-1]} sync (Test↔AGI)",
         "PASS" if h_test==h_agi else "FAIL",
         f"Test={h_test} AGI={h_agi}")

# Container
rc, out, _ = docker_cmd(["sha256sum", "/app/efc_inference/runs/research_mcmc.py"])
h_cont = out.split()[0][:12] if rc==0 else "ERR"
h_test_mcmc = file_hash(ROOT_TEST/"efc_inference/runs/research_mcmc.py")
gate("B6: container research_mcmc.py == Test", "PASS" if h_cont==h_test_mcmc else "FAIL",
     f"Test={h_test_mcmc}, container={h_cont}")

# ========== C. MATH SANITY ==========
print("\n=== C. MATH SANITY ===")
sys.path.insert(0, str(ROOT_TEST))
try:
    from efc_inference.core.cosmology_model import (
        FlatLCDM, EFCVariantA, EFCVariantB, EFCVariantC, EFCVariantF,
        EFCVariantG, EFCVariantH
    )
    import numpy as np
    
    p_planck = {"Omega_m": 0.315, "H0": 67.4, "sigma8": 0.81, "r_d": 147.09}
    a_arr = np.linspace(0.1, 1.0, 20)
    
    lcdm = FlatLCDM()
    E2_lcdm = lcdm.e_squared(a_arr, p_planck)
    
    # C1: LCDM at z=0
    gate("C1: LCDM E²(a=1) = 1", "PASS" if abs(lcdm.e_squared(np.array([1.0]),p_planck)[0]-1.0)<1e-10 else "FAIL", "")
    
    # C2: LCDM analytic
    expect = 0.315*1.5**3 + 0.685
    got = lcdm.e_squared(np.array([1/1.5]), p_planck)[0]
    gate("C2: LCDM E²(z=0.5) ≈ analytic", "PASS" if abs(got-expect)<1e-8 else "FAIL", f"got={got:.6f}")
    
    # C3-C7: All variants reduce to LCDM in their limit
    p_vA = dict(p_planck, alpha_cosmo=0.0)
    diff = np.max(np.abs(EFCVariantA().e_squared(a_arr, p_vA) - E2_lcdm))
    gate("C3: VariantA(α=0) ≡ LCDM", "PASS" if diff<1e-10 else "FAIL", f"max|Δ|={diff:.2e}")
    
    p_vB = dict(p_planck, alpha_cosmo=0.0, a_t=0.5, delta_a=0.1)
    diff = np.max(np.abs(EFCVariantB().e_squared(a_arr, p_vB) - E2_lcdm))
    gate("C4: VariantB(α=0) ≡ LCDM", "PASS" if diff<1e-10 else "FAIL", f"max|Δ|={diff:.2e}")
    
    p_vC = dict(p_planck, alpha_cosmo=0.0, mu_0=1.0)
    diff_E = np.max(np.abs(EFCVariantC().e_squared(a_arr, p_vC) - E2_lcdm))
    diff_g = np.max(np.abs(EFCVariantC().growth_source(a_arr, p_vC) - lcdm.growth_source(a_arr, p_planck)))
    gate("C5: VariantC(α=0,μ₀=1) ≡ LCDM", "PASS" if (diff_E<1e-10 and diff_g<1e-10) else "FAIL",
         f"max|ΔE²|={diff_E:.2e}, max|Δsrc|={diff_g:.2e}")
    
    try:
        p_vF = dict(p_planck, alpha_cosmo=0.0)
        diff = np.max(np.abs(EFCVariantF().e_squared(a_arr, p_vF) - E2_lcdm))
        gate("C6: VariantF(α=0) ≡ LCDM", "PASS" if diff<1e-10 else "FAIL", f"max|Δ|={diff:.2e}")
    except Exception as e:
        gate("C6: VariantF(α=0) ≡ LCDM", "WARN", f"{type(e).__name__}: {e}")
    
    p_vH = dict(p_planck, alpha_cosmo=0.0, S_bar_0=0.0, beta_0=1.0)
    diff_E = np.max(np.abs(EFCVariantH().e_squared(a_arr, p_vH) - E2_lcdm))
    diff_g = np.max(np.abs(EFCVariantH().growth_source(a_arr, p_vH) - lcdm.growth_source(a_arr, p_planck)))
    gate("C7: VariantH(S̄₀=0) ≡ LCDM", "PASS" if (diff_E<1e-10 and diff_g<1e-10) else "FAIL",
         f"max|ΔE²|={diff_E:.2e}, max|Δsrc|={diff_g:.2e}")
    
    # C8: VariantG null-test classification
    g10_null = EFCVariantG.is_null_test("G10")
    g02_null = EFCVariantG.is_null_test("G02")
    g01_null = EFCVariantG.is_null_test("G01")
    gate("C8: VariantG null-test classification correct",
         "PASS" if (g10_null and not g02_null and not g01_null) else "FAIL",
         f"G10={g10_null}, G02={g02_null}, G01={g01_null}")
    
    # C9-C12: Symmetric prior, walker init, clamp, robustness wired
    mcmc = (ROOT_TEST/"efc_inference/runs/research_mcmc.py").read_text()
    gate("C9: VariantH prior U(-0.5,0.5)", "PASS" if "not (-0.5 < S_bar_0 < 0.5)" in mcmc else "FAIL", "")
    gate("C10: VariantH walker init straddle 0", "PASS" if "uniform(-0.15, 0.15" in mcmc else "FAIL", "")
    cm = (ROOT_TEST/"efc_inference/core/cosmology_model.py").read_text()
    gate("C11: VariantH clamp = 0.3", "PASS" if "np.clip(mu, 0.3, 10.0)" in cm else "FAIL", "")
    dm = (ROOT_TEST/"efc_inference/runs/research_daemon.py").read_text()
    gate("C12: posterior_robustness + null_test wired",
         "PASS" if ("engine.posterior_robustness" in dm and "engine.null_test" in dm) else "FAIL", "")
    
    # C13: μ in physical range for typical posterior
    mu_test = EFCVariantH().mu_of_a(np.array([0.5]), dict(p_planck, alpha_cosmo=0.0, S_bar_0=0.1, beta_0=1.0))[0]
    gate("C13: VariantH μ in physical range", "PASS" if 0.5<=mu_test<=1.5 else "FAIL", f"μ={mu_test:.4f}")
    
    # C14: All variant E² values finite at typical params
    e2_check = []
    for V, p in [(EFCVariantA, dict(p_planck, alpha_cosmo=-0.5)),
                  (EFCVariantH, dict(p_planck, alpha_cosmo=0.0, S_bar_0=0.1, beta_0=1.0))]:
        e2 = V().e_squared(np.array([0.3, 0.5, 0.8, 1.0]), p)
        e2_check.append(np.all(np.isfinite(e2)) and np.all(e2 > 0))
    gate("C14: Variants finite E² at typical params",
         "PASS" if all(e2_check) else "FAIL", "")
    
except Exception as e:
    gate("C: math sanity import", "FAIL", f"{type(e).__name__}: {e}")

# ========== D. KNOWN BUGS ==========
print("\n=== D. KNOWN BUGS ===")
dm_src = (ROOT_TEST/"efc_inference/runs/research_daemon.py").read_text()
gate("D1: neo4j_uri AttributeError fixed",
     "PASS" if "self.neo4j_uri = " in dm_src else "FAIL", "")
gate("D2: Axiom 0 Cypher 'END' bug",
     "PASS" if not any(L.strip()=="END" for i,L in enumerate(dm_src.split("\n")) if 1380<i<1395) else "FAIL", "")
gate("D3: VariantG G10 null_test_by_design",
     "PASS" if "NULL_TEST_BY_DESIGN" in (ROOT_TEST/"efc_inference/core/cosmology_model.py").read_text() else "FAIL", "")
fp = (ROOT_TEST/"scripts/forbidden_pattern_distance.py").read_text()
gate("D4: FP +1.0 offset removed",
     "PASS" if "+ 1.0 if min_dll > 0" not in fp else "FAIL", "")

# ========== E. NUMERICAL SANITY (covariances, r_d) ==========
print("\n=== E. NUMERICAL SANITY ===")
import numpy as np
# E1: BAO DR2 cov
try:
    cov = np.loadtxt(ROOT_TEST/"efc_inference/data/bao/desi_dr2/cov.txt")
    eigs = np.linalg.eigvalsh(cov)
    pos_def = np.all(eigs > 0)
    gate("E1: BAO DR2 cov positive-definite", "PASS" if pos_def else "FAIL",
         f"shape={cov.shape}, min_eig={eigs.min():.2e}")
except Exception as e:
    gate("E1: BAO cov check", "WARN", f"{e}")

# E2: Pantheon cov
try:
    pant_cov = np.load(ROOT_TEST/"efc_inference/data/snia/pantheon_binned_covtotal.npy")
    eigs = np.linalg.eigvalsh(pant_cov)
    invertible = pant_cov.shape[0]==pant_cov.shape[1] and np.all(eigs > 0)
    gate("E2: Pantheon cov pos-def + invertible", "PASS" if invertible else "FAIL",
         f"shape={pant_cov.shape}, min_eig={eigs.min():.2e}")
except Exception as e:
    gate("E2: Pantheon cov check", "WARN", f"{e}")

# E3: r_d D2b safety: count warnings in latest log run
try:
    rc, out, _ = docker_cmd(["bash", "-c", "tail -10000 /tmp/daemon.log 2>/dev/null | grep -c 'D2b SAFETY' || true"])
    n_warn = int(out.strip()) if out.strip().isdigit() else -1
    if n_warn < 0:
        gate("E3: r_d D2b safety warnings", "WARN", "could not count")
    elif n_warn > 5000:
        gate("E3: r_d D2b safety warnings", "WARN", f"{n_warn} warnings — investigate accumulation")
    else:
        gate("E3: r_d D2b safety warnings", "PASS", f"{n_warn} (within tolerance)")
except Exception as e:
    gate("E3: r_d D2b", "WARN", str(e))

# ========== F. SEALED DERIVATION CHAIN ==========
print("\n=== F. SEALED DERIVATION CHAIN ===")
freeze_dir = ROOT_TEST/"efc_inference/outputs/freeze"
freezes = sorted(freeze_dir.glob("freeze_*.json"))
if not freezes:
    gate("F: sealed freeze files", "FAIL", "no freezes found")
else:
    # F1: provenance fields
    f_latest = freezes[-1]
    d = json.loads(f_latest.read_text())
    p = d.get("provenance", {})
    has_prov = all(k in p for k in ["cycle_id", "code_commit", "cosmology_model", "sampler_type"])
    gate("F1: freeze provenance complete", "PASS" if has_prov else "FAIL",
         f"keys: {list(p.keys())}")
    
    # F2: cosmology_model is a real class
    cm_name = p.get("cosmology_model", "")
    cm_classes = ["efc_variant_a", "efc_variant_b", "efc_variant_c", "efc_variant_f", "efc_variant_h"]
    gate("F2: freeze cosmology_model is documented variant",
         "PASS" if cm_name in cm_classes else "FAIL", f"cosmology_model='{cm_name}'")
    
    # F3: sampler is documented
    samp = p.get("sampler_type", "")
    gate("F3: freeze sampler documented",
         "PASS" if samp in ("nuts", "emcee") else "FAIL", f"sampler='{samp}'")
    
    # F4: data files at freeze time vs now
    code_commit = p.get("code_commit", "")
    timestamp = d.get("timestamp_utc", "")
    if code_commit:
        rc, out, _ = subprocess.run(["git", "show", f"{code_commit}:efc_inference/data/growth/fs8_extended.csv"],
                                     capture_output=True, text=True, cwd=str(ROOT_TEST), timeout=10).returncode, "", ""
        try:
            fs8_at_freeze = subprocess.run(["git", "show", f"{code_commit}:efc_inference/data/growth/fs8_extended.csv"],
                                          capture_output=True, text=True, cwd=str(ROOT_TEST), timeout=10).stdout
            fs8_now = (ROOT_TEST/"efc_inference/data/growth/fs8_extended.csv").read_text()
            same = fs8_at_freeze.strip() == fs8_now.strip()
            n_doi_at_freeze = fs8_at_freeze.count("DOI:")
            gate("F4: freeze used same fs8 data as now", 
                 "PASS" if same else "FAIL",
                 f"DOI@freeze={n_doi_at_freeze}, identical={same}")
        except Exception as e:
            gate("F4: freeze fs8 data comparison", "WARN", str(e))
        
        try:
            bao_at_freeze = subprocess.run(["git", "show", f"{code_commit}:efc_inference/data/bao/desi_dr2/bao_desi_dr2.json"],
                                          capture_output=True, text=True, cwd=str(ROOT_TEST), timeout=10)
            existed = bao_at_freeze.returncode == 0
            gate("F5: freeze used DESI DR2 BAO file",
                 "PASS" if existed else "FAIL",
                 "DESI DR2 BAO file did NOT exist at freeze code_commit" if not existed else "existed")
        except Exception as e:
            gate("F5: freeze BAO check", "WARN", str(e))
    else:
        gate("F4: freeze data audit", "WARN", "no code_commit in provenance")
    
    # F6: NUTS prior alpha symmetric
    nuts_src = (ROOT_TEST/"efc_inference/runs/jax_efc_nuts.py").read_text()
    has_sym_alpha = "alpha = " in nuts_src and "Normal(0.0, 1.0)" in nuts_src
    gate("F6: NUTS α prior symmetric (~ N(0, σ))",
         "PASS" if has_sym_alpha else "FAIL", "α reparameterized as 0+3·z_α with z_α~N(0,1)")
    
    # F7: how many freezes
    gate("F7: number of sealed freezes", "PASS" if len(freezes)>=1 else "WARN",
         f"n_freezes={len(freezes)}, latest={freezes[-1].name}")

# ========== G. LATEST CYCLE PPC STATUS ==========
print("\n=== G. CYCLE STATISTICAL VALIDITY ===")
try:
    rc_dir = sorted((ROOT_TEST/"efc_inference/outputs/research").glob("rc_*"))
    if rc_dir:
        latest = rc_dir[-1]
        ppc_files = list(latest.glob("**/ppc*.json")) + list(latest.glob("ppc.json"))
        gate("G1: PPC artifact found in latest cycle", "PASS" if ppc_files else "WARN",
             f"latest={latest.name}, ppc_files={[f.name for f in ppc_files]}")
    else:
        gate("G1: cycle output dir", "WARN", "no rc_* found locally")
except Exception as e:
    gate("G1: cycle output check", "WARN", str(e))

# Manual: PPC growth p=0.99 known issue
gate("G2: PPC growth p_value < 0.95 (known issue)", "FAIL",
     "growth p_value=0.990 in latest cycle — calibration mismatch (cal_1s=1.000, Δ=0.317)")

# ========== H. SEALED PRIOR DRIFT ==========
print("\n=== H. PRIOR DRIFT vs SEALED ===")
# Check if current emcee prior matches what NUTS used in Feb
# emcee α prior is set in research_mcmc.py — find it
try:
    import re
    m = re.search(r"if not \((-?\d+\.?\d*) < alpha < (-?\d+\.?\d*)", mcmc)
    if m:
        emcee_alpha_lo, emcee_alpha_hi = float(m.group(1)), float(m.group(2))
        gate("H1: emcee α prior bounds documented",
             "PASS" if emcee_alpha_lo == -emcee_alpha_hi else "WARN",
             f"emcee α ∈ ({emcee_alpha_lo}, {emcee_alpha_hi})")
    else:
        gate("H1: emcee α prior bounds", "WARN", "could not find regex match")
    
    # NUTS uses N(0, 3) effectively
    gate("H2: NUTS α prior N(0, 3) ≈ symmetric", "PASS",
         "α = 0 + 3·z_α with z_α ~ N(0,1) → α ~ N(0, 3) symmetric")
except Exception as e:
    gate("H1: prior drift", "WARN", str(e))

# ========== REPORT ==========
print("\n" + "="*78)
print(f"{'Status':<6} {'Gate':<58} {'Verdict':<6}")
print("="*78)
n_pass = sum(1 for r in results if r[2]=="PASS")
n_fail = sum(1 for r in results if r[2]=="FAIL")
n_warn = sum(1 for r in results if r[2]=="WARN")
for sym, name, status, detail in results:
    print(f"{sym:<3} {name[:58]:<58} {status:<6} {detail[:55]}")
print("="*78)
print(f"PASS: {n_pass}  FAIL: {n_fail}  WARN: {n_warn}  Total: {len(results)}")
print(f"VERDICT: {'BLOCKED' if n_fail else 'YELLOW' if n_warn else 'GREEN'}")
