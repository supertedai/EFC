#!/usr/bin/env python3
"""
run_efc_baseline.py
Kjører baseline EFC-kjøring for utvikling og debugging.

Leser:
- output/parameters.json

Produserer:
- output/run_metadata.json
- output/validation/rotation_curve.json
"""

import json
import subprocess
from datetime import datetime, UTC
from pathlib import Path

import numpy as np

from src.efc_core import EFCModel, load_parameters

ROOT = Path(__file__).resolve().parents[1]
PARAMS_PATH = ROOT / "output" / "parameters.json"
OUT_DIR = ROOT / "output" / "validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def get_git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
        ).decode().strip()
    except Exception:
        return "unknown"


def simple_rotation_curve(model: EFCModel):
    r = np.linspace(0.1, 20.0, 100)
    x = np.stack([r, np.zeros_like(r), np.zeros_like(r)], axis=-1)

    state = model.compute_state(x)
    Ef = state["Ef"]

    v = np.sqrt(np.abs(Ef))

    return {
        "r_kpc": r.tolist(),
        "v_model": v.tolist(),
    }


def main():
    if not PARAMS_PATH.exists():
        raise FileNotFoundError(f"Fant ikke parameterfil: {PARAMS_PATH}")

    params = load_parameters(PARAMS_PATH)
    model = EFCModel(params)

    result = simple_rotation_curve(model)

    out_json = OUT_DIR / "rotation_curve.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    meta = {
        "timestamp": datetime.now(UTC).isoformat(),
        "git_commit": get_git_commit(),
        "params": str(PARAMS_PATH),
    }

    meta_path = ROOT / "output" / "run_metadata.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("[EFC] Baseline run fullført.")
    print(f"- rotation curve: {out_json}")
    print(f"- metadata: {meta_path}")


if __name__ == "__main__":
    main()
