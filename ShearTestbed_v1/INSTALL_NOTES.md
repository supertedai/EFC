# KCAP/CosmoSIS Installation Notes

This document describes the installation of KCAP (KiDS Cosmology Analysis Pipeline) with CosmoSIS for the EFC ShearTestbed.

## Components Installed

1. **CosmoSIS Standalone** (v0.2.2)
   - Core CosmoSIS framework from PyPI
   - Fortran modules rebuilt with KCAP-specific section names
   - Location: `/usr/local/lib/python3.11/dist-packages/cosmosis/`

2. **KCAP** (KiDS-WL/kcap)
   - Full KCAP repository with cosmosis-standard-library
   - Location: `/home/user/EFC/ShearTestbed_v1/kcap/`

## Built Modules

The following CosmoSIS modules were built:
- boltzmann/camb - CAMB interface for power spectra
- boltzmann/halofit - Halofit non-linear power spectrum
- boltzmann/halofit_takahashi - Takahashi Halofit variant
- structure/cosmic_emu - Cosmic emulator
- structure/meadcb - Mead CB structure
- structure/projection - Angular power spectrum projection
- shear/cl_to_xi_nicaea - C_ell to xi conversion
- likelihood/planck2018 - Planck 2018 likelihood
- cosebis - COSEBIs (Complete Orthogonal Sets of E/B Integrals)

## System Dependencies

The following system packages were installed:
- gcc, g++, gfortran (compilers)
- libgsl-dev (GNU Scientific Library)
- libfftw3-dev (Fast Fourier Transform)
- libcfitsio-dev (FITS I/O)
- liblapack-dev, libblas-dev (Linear algebra)
- libopenblas-dev (Optimized BLAS)

## Python Dependencies

- numpy, scipy, astropy
- camb (Python CAMB interface)
- emcee (MCMC sampler)
- mpi4py (MPI bindings)
- pyyaml, future, setuptools

## Configuration Files

KCAP configuration files are available at:
`/home/user/EFC/ShearTestbed_v1/kcap/runs/config/`

Key configurations:
- KV450_fiducial.ini - Fiducial KV450 cosmic shear analysis
- KV450_no_sys.ini - KV450 without systematics
- BOSS_KV450.ini - Combined BOSS + KV450 3x2pt

## Usage

To run a CosmoSIS pipeline:
```bash
cd /home/user/EFC/ShearTestbed_v1/kcap
cosmosis runs/config/KV450_no_sys.ini
```

## Notes

- The installation was performed with `--no-mpi` flag (no MPI support)
- Fortran modules were rebuilt with custom section names for KCAP compatibility
- For full KiDS-1000 analysis, additional data files may be required

## Date

Installation completed: 2026-02-05
