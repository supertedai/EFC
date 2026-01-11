"""
sparc_io.py
<<<<<<< HEAD
Robust innlesing av SPARC-rotasjonskurver (R, Vobs, eV ...).
Finner kolonner ved å inspisere headerlinjen.
"""
=======
Robust innlesing av SPARC-rotasjonskurver (R, Vobs, eV).
"""

>>>>>>> 6fe47b1 (Add complete SPARC validation pipeline + parsers + EFC baseline integration)
from pathlib import Path
import numpy as np

CANDIDATE_R = ["R", "Rkpc", "R(kpc)"]
CANDIDATE_V = ["Vobs", "Vrot", "V", "V(km/s)"]
CANDIDATE_eV = ["eV", "e_V", "e(V)", "eVrot"]

def _find_cols(header_tokens):
    def pick(cands):
        for c in cands:
            if c in header_tokens:
                return header_tokens.index(c)
        return None
    iR = pick(CANDIDATE_R)
    iV = pick(CANDIDATE_V)
    ie = pick(CANDIDATE_eV)
    return iR, iV, ie

def load_rotation_curve(file_path: Path):
    lines = file_path.read_text().strip().splitlines()
<<<<<<< HEAD
    # finn første ikke-kommentar-linje som header
=======

>>>>>>> 6fe47b1 (Add complete SPARC validation pipeline + parsers + EFC baseline integration)
    header = None
    for ln in lines:
        if ln.strip().startswith("#"):
            continue
        header = ln
        break
<<<<<<< HEAD
    if header is None:
        raise ValueError(f"Mangler header i {file_path}")
    header_tokens = header.strip().split()
    iR, iV, ie = _find_cols(header_tokens)
    if iR is None or iV is None:
        raise ValueError(f"Fant ikke R/V-kolonner i {file_path}. Header: {header_tokens}")

    data = []
    started = False
=======

    if header is None:
        raise ValueError(f"Mangler header i {file_path}")

    header_tokens = header.split()
    iR, iV, ie = _find_cols(header_tokens)

    if iR is None or iV is None:
        raise ValueError(f"Fant ikke R/V-kolonner i {file_path}")

    data = []
    started = False

>>>>>>> 6fe47b1 (Add complete SPARC validation pipeline + parsers + EFC baseline integration)
    for ln in lines:
        if not started:
            if ln.strip() == header:
                started = True
            continue
<<<<<<< HEAD
        if ln.strip().startswith("#") or not ln.strip():
            continue
        toks = ln.split()
=======
        if ln.startswith("#") or not ln.strip():
            continue

        toks = ln.split()

>>>>>>> 6fe47b1 (Add complete SPARC validation pipeline + parsers + EFC baseline integration)
        try:
            R = float(toks[iR])
            V = float(toks[iV])
            e = float(toks[ie]) if ie is not None and ie < len(toks) else np.nan
            data.append((R, V, e))
<<<<<<< HEAD
        except Exception:
            # hopp over linjer som ikke parser
            continue
    arr = np.array(data, dtype=float)
    if arr.size == 0:
        raise ValueError(f"Ingen data lest fra {file_path}")
    R = arr[:,0]   # kpc
    V = arr[:,1]   # km/s
    eV = arr[:,2]  # km/s (kan være NaN)
    return R, V, eV
=======
        except:
            continue

    arr = np.array(data, dtype=float)
    if arr.size == 0:
        raise ValueError(f"Ingen data lest fra {file_path}")

    return arr[:,0], arr[:,1], arr[:,2]
>>>>>>> 6fe47b1 (Add complete SPARC validation pipeline + parsers + EFC baseline integration)
