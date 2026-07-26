"""
SPARC Rotation Curve Module

Loads SPARC galaxy rotation curve data and computes likelihood
against EFC rotation velocity predictions.

Data source:
    - supertedai/EFC repo: docs/papers/efc/Comprehensive-analysis-.../
      sparc-n175-extended/sparc_rotation_curves.dat (175 galaxies)
    - Or individual galaxy files via sparc_io.py

Usage:
    engine = EFCRotation()
    module = SPARCModule(engine)
    module.load_data(data_path="path/to/sparc_rotation_curves.dat",
                     galaxy="NGC2403")
    ll = module.log_likelihood(params_dict)
"""

import numpy as np
from pathlib import Path
from typing import Optional
import logging

from .base_module import BaseModule
from ..engine.rotation import EFCRotation

logger = logging.getLogger(__name__)


class SPARCModule(BaseModule):
    """
    SPARC galaxy rotation curve module.

    Supports two data formats:
    1. Multi-galaxy file (sparc_rotation_curves.dat) — select by galaxy name
    2. Single-galaxy file via sparc_io.py loader
    """

    def __init__(self, engine: Optional[EFCRotation] = None):
        if engine is None:
            engine = EFCRotation()
        super().__init__(engine)
        self.galaxy_name: Optional[str] = None
        self._all_galaxies: Optional[dict] = None

    @property
    def name(self) -> str:
        if self.galaxy_name:
            return f"sparc_{self.galaxy_name}"
        return "sparc"

    def load_data(self, data_path: str = None, galaxy: str = None,
                  min_error: float = 1.0, **kwargs):
        """
        Load SPARC rotation curve data.

        Parameters:
            data_path: Path to sparc_rotation_curves.dat or individual file
            galaxy:    Galaxy name (for multi-galaxy file)
            min_error: Minimum velocity error floor in km/s (default 1.0)
        """
        if data_path is None:
            raise ValueError("data_path is required")

        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"SPARC data not found: {path}")

        self.galaxy_name = galaxy

        # Try multi-galaxy format first
        if galaxy is not None:
            self._load_multi_galaxy(path, galaxy, min_error)
        else:
            self._load_single_galaxy(path, min_error)

        self._loaded = True
        logger.info(f"Loaded SPARC data: {self.galaxy_name or 'unknown'}, "
                    f"{self.n_data} data points")

    def _load_multi_galaxy(self, path: Path, galaxy: str,
                           min_error: float):
        """Load from multi-galaxy sparc_rotation_curves.dat format."""
        text = path.read_text()
        lines = text.strip().splitlines()

        # Parse: galaxy_name distance radius Vobs eV Vgas Vdisk Vbul SBdisk SBbul
        radii = []
        vobs = []
        verr = []
        found = False

        for line in lines:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            if len(parts) < 5:
                continue

            gal_name = parts[0]
            if gal_name != galaxy:
                if found:
                    break  # Past this galaxy's data
                continue

            found = True
            try:
                r = float(parts[2])    # radius in kpc
                v = float(parts[3])    # Vobs in km/s
                e = float(parts[4])    # eV in km/s
                if e < min_error:
                    e = min_error
                radii.append(r)
                vobs.append(v)
                verr.append(e)
            except (ValueError, IndexError):
                continue

        if not found:
            raise ValueError(f"Galaxy '{galaxy}' not found in {path}")

        self.coordinates = np.array(radii)
        self.observed = np.array(vobs)
        self.errors = np.array(verr)

    def _load_single_galaxy(self, path: Path, min_error: float):
        """Load from single-galaxy file via sparc_io.py."""
        import sys
        src_path = str(Path(__file__).resolve().parents[2] / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            from efc.validation.sparc_io import load_rotation_curve
            R, V, eV = load_rotation_curve(path)

            # Floor errors
            eV = np.where(np.isnan(eV), min_error, eV)
            eV = np.maximum(eV, min_error)

            self.coordinates = R
            self.observed = V
            self.errors = eV
            self.galaxy_name = path.stem

        except ImportError:
            # Fallback: try to parse as whitespace-delimited R V eV
            data = np.loadtxt(path, comments="#")
            if data.shape[1] >= 3:
                self.coordinates = data[:, 0]
                self.observed = data[:, 1]
                self.errors = np.maximum(data[:, 2], min_error)
            else:
                raise ValueError(f"Cannot parse {path} — need at least 3 columns")

    def available_galaxies(self, data_path: str) -> list[str]:
        """List all galaxy names in a multi-galaxy data file."""
        path = Path(data_path)
        galaxies = set()
        for line in path.read_text().splitlines():
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            if parts:
                galaxies.add(parts[0])
        return sorted(galaxies)

    def _params_from_array(self, arr: np.ndarray) -> dict:
        """Map flat array to rotation engine parameters."""
        names = ["entropy_scale", "length_scale", "flow_constant", "velocity_scale"]
        return {names[i]: arr[i] for i in range(min(len(arr), len(names)))}
