"""Minimal reproducer: load data and re-fit LCDM and EFC."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from efc_multi_epoch_v2 import load_data, fit_LCDM, fit_EFC

z, f, s = load_data()
lcdm = fit_LCDM(z, f, s)
print("LCDM:", lcdm)
efc = fit_EFC(z, f, s, Om_fixed=lcdm["Omega_m"])
print("EFC :", efc)
print("delta_chi2 =", efc["chi2"] - lcdm["chi2"])
