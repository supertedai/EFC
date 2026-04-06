#!/usr/bin/env python3
"""
Demo: EFC Entropy Budget Working Note
DOI: 10.6084/m9.figshare.31942734

Demonstrates the cosmic entropy budget as constraint on the EFC S-field.
"""

import sys, os, math

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.entropy_budget import (
    CosmicEntropyInventory,
    BekensteinHawkingEntropy,
    GRCTriadMapping,
    SFieldNormalization,
    ThermostatConjecture,
    Predictions,
    M_SUN,
    K_B,
)


def demo_1_entropy_inventory():
    """Table 1: Cosmic entropy budget."""
    print("=" * 65)
    print("Demo 1: Cosmic Entropy Inventory (Table 1)")
    print("=" * 65)

    inv = CosmicEntropyInventory()

    print(f"\n{'Component':<30} {'log10(S/k_B)':<15} {'S-field regime'}")
    print("-" * 65)
    for c in inv.components:
        print(f"{c.name:<30} {c.log10_entropy_kB:<15.1f} {c.s_field_regime}")

    dominant = inv.dominant_component()
    frac = inv.smbh_fraction()
    print(f"\nDominant component: {dominant.name}")
    print(f"SMBH fraction of total entropy: {frac:.6f} (>{99.99}%)")
    print(f"Total entropy: ~10^{math.log10(inv.total_entropy_kB()):.1f} k_B")

    assert frac > 0.99, "SMBH should dominate entropy budget"
    assert dominant.name == "Supermassive black holes"
    print("\n✓ SMBH dominance confirmed")


def demo_2_bekenstein_hawking():
    """Bekenstein-Hawking entropy for representative SMBHs."""
    print("\n" + "=" * 65)
    print("Demo 2: Bekenstein-Hawking Entropy")
    print("=" * 65)

    bh = BekensteinHawkingEntropy()

    masses = {
        "Sgr A* (4×10^6 M☉)": 4e6 * M_SUN,
        "M87* (6.5×10^9 M☉)": 6.5e9 * M_SUN,
        "TON 618 (6.6×10^10 M☉)": 6.6e10 * M_SUN,
    }

    print(f"\n{'Black hole':<30} {'Mass (kg)':<15} {'log10(S/k_B)':<15} {'A (m²)'}")
    print("-" * 65)
    for name, mass in masses.items():
        s = bh.entropy_kB(mass)
        a = bh.horizon_area(mass)
        print(f"{name:<30} {mass:<15.3e} {math.log10(s):<15.1f} {a:.3e}")

    # Verify consistency: S from mass vs S from area
    m_test = 1e9 * M_SUN
    s_mass = bh.entropy_kB(m_test)
    a_test = bh.horizon_area(m_test)
    s_area = bh.entropy_from_area(a_test)
    ratio = s_mass / s_area
    print(f"\nConsistency check (10^9 M☉): S(M)/S(A) = {ratio:.4f}")
    assert abs(ratio - 1.0) < 0.01, "Mass and area formulas should agree"

    # Inverse: mass from entropy
    m_recovered = bh.mass_from_entropy_kB(s_mass)
    print(f"Inverse check: M_recovered/M_input = {m_recovered/m_test:.6f}")
    assert abs(m_recovered / m_test - 1.0) < 1e-6
    print("✓ Bekenstein-Hawking formulas consistent")


def demo_3_grc_triad():
    """Table 2: GRC triad configurations."""
    print("\n" + "=" * 65)
    print("Demo 3: GRC Triad Mapping (Table 2)")
    print("=" * 65)
    print("Reality = Grid ⊗ Energy · Clarity(S)\n")

    grc = GRCTriadMapping()

    print(f"{'Phenomenon':<25} {'Grid':<20} {'Clarity (S)'}")
    print("-" * 65)
    for cfg in grc.all_configurations():
        print(f"{cfg.phenomenon:<25} {cfg.grid_state:<20} {cfg.clarity_S}")

    print("\nS-field hierarchy (low → high):")
    for key, s_val in grc.s_field_hierarchy():
        print(f"  {key:<15} → {s_val}")

    # Verify BH is at S_max
    bh_cfg = grc.get("black_holes")
    assert "S_max" in bh_cfg.clarity_S
    print("\n✓ Black holes correctly at S = S_max (grid collapse)")


def demo_4_s_field_normalization():
    """S-field mapping: S_EFC/S_max = (M/M_max)²."""
    print("\n" + "=" * 65)
    print("Demo 4: S-Field Normalization (Eq. 2)")
    print("=" * 65)

    sf = SFieldNormalization()

    # M_max ~ largest known SMBH mass as reference
    m_max = 1e11 * M_SUN  # ~10^11 M_sun upper bound

    test_masses = [
        ("Sgr A*", 4e6 * M_SUN),
        ("M87*", 6.5e9 * M_SUN),
        ("TON 618", 6.6e10 * M_SUN),
        ("Hypothetical M_max", m_max),
    ]

    print(f"\n{'Object':<25} {'M/M_max':<15} {'S_EFC/S_max':<15} {'Grid collapse?'}")
    print("-" * 65)
    for name, mass in test_masses:
        r = sf.ratio(mass, m_max)
        collapse = sf.grid_collapse_condition(mass, m_max)
        print(f"{name:<25} {mass/m_max:<15.2e} {r:<15.2e} {collapse}")

    # At M = M_max, ratio should be 1.0
    assert sf.ratio(m_max, m_max) == 1.0
    assert sf.grid_collapse_condition(m_max, m_max)
    print("\n✓ S_EFC/S_max = 1 at M = M_max (grid collapse confirmed)")


def demo_5_thermostat():
    """Thermostat conjecture: AGN decline drives S(z) sigmoid."""
    print("\n" + "=" * 65)
    print("Demo 5: SMBH Thermostat Conjecture")
    print("=" * 65)

    tc = ThermostatConjecture()

    # Accretion luminosity for 1 M_sun/yr
    mdot = 1.0 * M_SUN / (3.156e7)  # 1 M_sun/yr in kg/s
    L_acc = tc.accretion_luminosity(mdot)
    print(f"\nAccretion at 1 M☉/yr:")
    print(f"  L_acc = {L_acc:.3e} W  (η = 0.1)")
    print(f"  log10(L_acc) = {math.log10(L_acc):.1f}")

    # Entropy production rate
    T_acc = 1e7  # K, typical accretion disk temperature
    s_dot = tc.entropy_production_rate(L_acc, T_acc)
    print(f"  Ṡ_acc = {s_dot:.3e} k_B/s  (at T_acc = 10^7 K)")

    # AGN luminosity density vs redshift
    print(f"\n{'z':<8} {'ρ_L (W/Mpc³)':<18} {'S(z)/S_max'}")
    print("-" * 45)
    for z in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        rho = tc.agn_luminosity_density(z)
        s_z = tc.s_field_sigmoid(z)
        print(f"{z:<8.1f} {rho:<18.3e} {s_z:<.4f}")

    # S(z) should transition around z ~ 1
    s_low = tc.s_field_sigmoid(0.0)
    s_mid = tc.s_field_sigmoid(1.0)
    s_high = tc.s_field_sigmoid(3.0)
    assert s_low < 0.2, f"S(z=0) should be low, got {s_low}"
    assert abs(s_mid - 0.5) < 0.01, f"S(z=1) should be ~0.5, got {s_mid}"
    assert s_high > 0.95, f"S(z=3) should be high, got {s_high}"

    print(f"\nTransition parameters: {tc.transition_redshift()}")
    print("✓ S(z) sigmoid transition confirmed at z ~ 1")


def demo_6_predictions():
    """Predictions P1–P4 and open gaps G1–G4."""
    print("\n" + "=" * 65)
    print("Demo 6: Predictions & Open Gaps")
    print("=" * 65)

    pred = Predictions()

    print("\nPredictions:")
    for p in pred.predictions:
        print(f"  {p.id}: {p.description}")
        print(f"       Observable: {p.observable}")

    print("\nOpen Gaps:")
    for g in pred.open_gaps:
        print(f"  {g.id} [{g.level}]: {g.description}")

    assert len(pred.predictions) == 4
    assert len(pred.open_gaps) == 4
    assert pred.get_prediction("P2").description == "S(z) tracks AGN luminosity density"
    assert pred.get_gap("G3").level == "L3"
    print("\n✓ All predictions and gaps verified")


if __name__ == "__main__":
    print("EFC Entropy Budget Working Note — Demo")
    print("DOI: 10.6084/m9.figshare.31942734\n")

    demo_1_entropy_inventory()
    demo_2_bekenstein_hawking()
    demo_3_grc_triad()
    demo_4_s_field_normalization()
    demo_5_thermostat()
    demo_6_predictions()

    print("\n" + "=" * 65)
    print("All demos passed successfully.")
    print("=" * 65)
