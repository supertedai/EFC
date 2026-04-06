#!/usr/bin/env python3
"""Demo: AI-Augmented Scientific Workflow Framework.

Shows how the EFC workflow manages stages, validation layers, and
reproducibility metadata.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.workflow_framework import (
    ScientificWorkflow,
    WorkflowStage,
    ValidationLayer,
    Role,
)


def main():
    print("=" * 60)
    print("EFC -- AI-Augmented Scientific Workflow: Demo")
    print("=" * 60)

    # Build default workflow
    wf = ScientificWorkflow("EFC-Phenomenological-Law", author="Morten Magnusson")
    wf.build_default()
    print(f"\nWorkflow: {wf}")
    print(f"Stages: {len(wf.stages)}")
    print(f"Validation layers: {len(wf.validations)}")

    # Show stages
    print(f"\n{'Stage':<20} {'Role':<8} {'Status':<10}")
    print("-" * 40)
    for stage in wf.stages:
        status = "done" if stage.completed else "pending"
        print(f"{stage.name:<20} {stage.role.value:<8} {status:<10}")

    # Simulate completing stages
    print("\n--- Simulating workflow execution ---")
    for stage in wf.stages[:4]:
        stage.complete(passed=True)
        print(f"Completed: {stage.name} ({stage.role.value})")

    print(f"\nProgress: {wf.progress():.0%}")
    print(f"Completed: {wf.completed_stages()}")
    print(f"Pending:   {wf.pending_stages()}")

    # Validation
    print("\n--- Validation Layers ---")
    efc_d = wf.validations[0]
    efc_d.evaluate("mathematical_consistency", True, "Equations verified")
    efc_d.evaluate("dimensional_analysis", True, "All dimensions match")
    efc_d.evaluate("limit_recovery", True, "GR recovered at early times")
    print(f"{efc_d}: {efc_d.summary()}")

    # Summary
    print("\n--- Full Summary ---")
    summary = wf.summary()
    print(json.dumps(summary, indent=2))

    # Verification
    print("\n--- Verification ---")
    assert wf.progress() > 0.0, "Some stages must be completed"
    assert len(wf.completed_stages()) == 4
    assert len(wf.pending_stages()) == 3
    assert efc_d.all_passed(), "EFC-D should pass all criteria"

    custom_stage = WorkflowStage("custom", Role.HUMAN, "A custom stage",
                                 inputs=["a", "b"], outputs=["c"])
    assert not custom_stage.is_ready(["a"]), "Missing input b"
    assert custom_stage.is_ready(["a", "b"]), "All inputs available"

    print("All checks passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
