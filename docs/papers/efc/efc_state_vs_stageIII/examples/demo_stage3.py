#!/usr/bin/env python3
"""
Demo: EFC vs Stage-III Cosmology State Assessment

Evaluates EFC's position in the post-tension weak-lensing landscape.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.state_vs_stage3 import StageIIIAssessment, SCELayerClassification, PAPER_RESULTS


def main():
    print("=" * 65)
    print("EFC vs Stage-III Cosmology State Assessment")
    print("=" * 65)

    assessment = StageIIIAssessment()

    # --- Stage-III observations ---
    print("\n1. STAGE-III WEAK-LENSING OBSERVATIONS")
    print("-" * 45)
    obs = PAPER_RESULTS['stage_iii_observations']
    for survey, data in obs.items():
        s8 = data['S8']
        err = data.get('err', data.get('err_plus', '?'))
        print(f"   {survey:<25} S8 = {s8} +/- {err}")

    # --- EFC position ---
    print("\n2. EFC POSITION ASSESSMENT")
    print("-" * 45)
    result = assessment.evaluate_efc_position()
    print(f"   EFC sigma8 = {result['efc_sigma8']}")
    print(f"   EFC beta = {result['efc_beta']}")
    for m in result['measurements']:
        print(f"   vs {m['survey']:<25} pull = {m['pull_from_efc']:<10} "
              f"{'OK' if m['consistent'] else 'TENSION'}")
    print(f"\n   {result['sigma8_comparison']}")

    # --- Narrative update ---
    print("\n3. NARRATIVE UPDATE")
    print("-" * 45)
    narr = assessment.narrative_update()
    print(f"   DEPRECATED: {narr['deprecated']}")
    print(f"   CURRENT:    {narr['current'][:80]}...")
    print(f"   FROM: {narr['category_from']}")
    print(f"   TO:   {narr['category_to']}")

    # --- SCE layer classification ---
    print("\n4. SCE LAYER CLASSIFICATION")
    print("-" * 45)
    sce = SCELayerClassification()
    print(f"   O-layer ({sce.O_LAYER['name']}):")
    for ex in sce.O_LAYER['examples']:
        print(f"     - {ex}")
    print(f"   M-layer ({sce.M_LAYER['name']}):")
    print(f"     S8 assumes: {', '.join(sce.M_LAYER['S8_assumptions'][:3])}...")

    # --- Stage-IV tests ---
    print("\n5. STAGE-IV DISCRIMINATING TESTS")
    print("-" * 45)
    tests = assessment.stage_iv_tests()
    for t in tests:
        print(f"   {t['test']}")
        print(f"     EFC:  {t['efc']}")
        print(f"     LCDM: {t['lcdm']}")
        print(f"     Data: {t['data']}")

    # --- Strengths ---
    print("\n6. EFC STRENGTHS IN NEW LANDSCAPE")
    print("-" * 45)
    for s in PAPER_RESULTS['strengths']:
        print(f"   - {s}")

    print("\n" + "=" * 65)
    print("EFC reframed as precision structural competitor, not tension fixer.")
    print("=" * 65)


if __name__ == '__main__':
    main()
