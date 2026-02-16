"""
Cubic lattice graph construction for discrete gravity.

Builds an N^3 cubic lattice where each interior node connects to its
six nearest neighbours. Boundary nodes connect to fewer.
"""

import numpy as np
from typing import List, Tuple, Dict


class CubicGraph:
    """N^3 cubic lattice graph with nearest-neighbour connectivity."""

    def __init__(self, N: int, spacing: float = 1.0):
        """
        Parameters
        ----------
        N : int
            Lattice dimension (total nodes = N^3).
        spacing : float
            Lattice spacing `a`.
        """
        self.N = N
        self.spacing = spacing
        self.total_nodes = N ** 3

    def node_index(self, ix: int, iy: int, iz: int) -> int:
        """Convert 3D coordinates to flat index."""
        return ix * self.N * self.N + iy * self.N + iz

    def node_coords(self, idx: int) -> Tuple[int, int, int]:
        """Convert flat index to 3D coordinates."""
        ix = idx // (self.N * self.N)
        iy = (idx % (self.N * self.N)) // self.N
        iz = idx % self.N
        return (ix, iy, iz)

    def neighbours(self, idx: int) -> List[int]:
        """Return list of neighbour indices for node idx."""
        ix, iy, iz = self.node_coords(idx)
        nbrs = []
        for dix, diy, diz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            nx, ny, nz = ix + dix, iy + diy, iz + diz
            if 0 <= nx < self.N and 0 <= ny < self.N and 0 <= nz < self.N:
                nbrs.append(self.node_index(nx, ny, nz))
        return nbrs

    def distance_from_center(self, idx: int) -> float:
        """Euclidean distance from node to lattice center in units of spacing."""
        ix, iy, iz = self.node_coords(idx)
        cx = (self.N - 1) / 2.0
        return np.sqrt((ix - cx)**2 + (iy - cx)**2 + (iz - cx)**2) * self.spacing


def build_lattice(N: int, spacing: float = 1.0) -> CubicGraph:
    """Build an N^3 cubic lattice graph."""
    return CubicGraph(N, spacing)
