"""
Demo: AI Workflow Framework for Energy-Flow Cosmology.

Demonstrates the workflow pipeline construction, execution,
role-based querying, and validation pipeline.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ai_workflow import (
    AIWorkflowFramework,
    Role,
    ValidationPipeline,
    WorkflowStage,
)


def main():
    print("=" * 60)
    print("AI Workflow Framework - Demo")
    print("=" * 60)

    # 1. Build default pipeline
    print("\n--- Build Default Pipeline ---")
    fw = AIWorkflowFramework(name="EFC AI Workflow", version="1.0")
    fw.build_default_pipeline()
    for stage in fw.stages:
        print(f"  [{stage.role.value}] {stage.name}")
        print(f"    In:  {stage.inputs}")
        print(f"    Out: {stage.outputs}")

    # 2. Execute pipeline
    print("\n--- Execute Pipeline ---")
    results = fw.run()
    for stage_name, status in results.items():
        print(f"  {stage_name}: {status}")

    # 3. Query by role
    print("\n--- Stages by Role ---")
    for role in Role:
        stages = fw.get_stages_by_role(role)
        names = [s.name for s in stages]
        print(f"  {role.value}: {names}")

    # 4. Validation pipeline demo
    print("\n--- Validation Pipeline ---")
    pipeline = ValidationPipeline()
    pipeline.add_check("has_title", lambda: True)
    pipeline.add_check("has_doi", lambda: True)
    pipeline.add_check("schema_valid", lambda: True)
    all_pass = pipeline.run_all()
    print(f"  All checks pass: {all_pass}")
    for name, result in pipeline.summary().items():
        print(f"    {name}: {'PASS' if result else 'FAIL'}")

    # 5. Load reference data
    print("\n--- Reference Data ---")
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "ai_workflow_data.json"
    )
    with open(data_path) as f:
        data = json.load(f)
    print(f"  Roles defined: {len(data['roles'])}")
    print(f"  Pipeline stages: {len(data['default_pipeline'])}")
    print(f"  AI boundaries - may not: {data['boundaries']['ai_may_not']}")

    # 6. Summary
    print("\n--- Framework Summary ---")
    summary = fw.summary()
    print(f"  Name: {summary['name']}")
    print(f"  Version: {summary['version']}")
    print(f"  Stages: {summary['n_stages']}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
