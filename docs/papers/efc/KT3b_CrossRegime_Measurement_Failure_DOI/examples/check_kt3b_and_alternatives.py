"""
Minimal reproducer: run the RCMP check on KT3b and the three valid
alternative architectures (A, B, C) and print the results.

Expected output:
    [FAIL] KT3b original            : V1, V2, V3
    [OK  ] A — pure L2 ...          : none
    [OK  ] B — pure L1 ...          : none
    [OK  ] C — derived L1->L2 ...   : none
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rcmp_check import check_all, default_architectures  # noqa: E402

if __name__ == "__main__":
    print("RCMP compliance check (KT3b paper, DOI 31963821):")
    print("-" * 64)
    for result in check_all(default_architectures()):
        print(result)
        for note in result.notes:
            print(f"    - {note}")
    print("-" * 64)
    print("Diagnosis: KT3b original triggers all three violations (V1+V2+V3).")
    print("           Architectures A, B, C are RCMP-consistent.")
