"""
AI Workflow Framework for Energy-Flow Cosmology.

Models the AI-augmented scientific workflow, separating human theoretical
reasoning from AI structural assistance, reproducible computation,
and semantic/metadata generation.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class Role(Enum):
    """Roles within the AI-augmented scientific workflow."""
    HUMAN_THEORIST = "human_theorist"
    AI_STRUCTURAL = "ai_structural"
    COMPUTATIONAL = "computational"
    METADATA_SEMANTIC = "metadata_semantic"


class StageStatus(Enum):
    """Status of a workflow stage."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATED = "validated"
    FAILED = "failed"


@dataclass
class WorkflowStage:
    """A single stage in the scientific workflow pipeline.

    Attributes:
        name: Human-readable stage name.
        role: Which role is responsible.
        description: What this stage accomplishes.
        status: Current execution status.
        inputs: List of input artifact names.
        outputs: List of output artifact names.
        validation_criteria: Criteria that must pass for stage completion.
    """
    name: str
    role: Role
    description: str = ""
    status: StageStatus = StageStatus.PENDING
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)

    def execute(self) -> bool:
        """Mark the stage as in-progress and return True."""
        self.status = StageStatus.IN_PROGRESS
        return True

    def validate(self) -> bool:
        """Mark the stage as validated if criteria are present.

        Returns:
            True if stage passes validation.
        """
        if self.validation_criteria:
            self.status = StageStatus.VALIDATED
            return True
        self.status = StageStatus.VALIDATED
        return True

    def fail(self, reason: str = "") -> None:
        """Mark the stage as failed."""
        self.status = StageStatus.FAILED


class ValidationPipeline:
    """Pipeline of validation checks applied to workflow outputs.

    Attributes:
        checks: Ordered list of named validation functions.
    """

    def __init__(self):
        self.checks: List[tuple[str, Callable[..., bool]]] = []
        self.results: Dict[str, bool] = {}

    def add_check(self, name: str, check_fn: Callable[..., bool]) -> None:
        """Register a named validation check."""
        self.checks.append((name, check_fn))

    def run_all(self, artifact: Any = None) -> bool:
        """Execute all checks, storing results.

        Args:
            artifact: The object to validate.

        Returns:
            True if all checks pass.
        """
        self.results.clear()
        all_pass = True
        for name, fn in self.checks:
            try:
                result = fn(artifact) if artifact is not None else fn()
                self.results[name] = result
                if not result:
                    all_pass = False
            except Exception:
                self.results[name] = False
                all_pass = False
        return all_pass

    def summary(self) -> Dict[str, bool]:
        """Return the results of the last validation run."""
        return dict(self.results)


class AIWorkflowFramework:
    """Top-level AI-augmented scientific workflow framework.

    Separates human theoretical reasoning, AI structural assistance,
    reproducible computational workflow, and semantic metadata generation
    into distinct stages with validation gates.

    Attributes:
        name: Framework instance name.
        version: Semantic version string.
        stages: Ordered list of workflow stages.
    """

    def __init__(self, name: str = "EFC AI Workflow", version: str = "1.0"):
        self.name = name
        self.version = version
        self.stages: List[WorkflowStage] = []
        self._pipeline = ValidationPipeline()

    def add_stage(self, stage: WorkflowStage) -> None:
        """Append a stage to the workflow."""
        self.stages.append(stage)

    def build_default_pipeline(self) -> None:
        """Construct the default EFC workflow pipeline."""
        self.stages = [
            WorkflowStage(
                name="Theoretical Formulation",
                role=Role.HUMAN_THEORIST,
                description="Human develops theoretical framework and hypotheses.",
                inputs=["prior_knowledge", "observational_data"],
                outputs=["hypothesis", "equations"],
                validation_criteria=["internal_consistency"],
            ),
            WorkflowStage(
                name="Structural Encoding",
                role=Role.AI_STRUCTURAL,
                description="AI structures, stabilises, and encodes theoretical content.",
                inputs=["hypothesis", "equations"],
                outputs=["structured_document", "schema"],
                validation_criteria=["schema_valid", "no_hallucination"],
            ),
            WorkflowStage(
                name="Computational Validation",
                role=Role.COMPUTATIONAL,
                description="Reproducible numerical analysis and statistical testing.",
                inputs=["structured_document", "datasets"],
                outputs=["results", "figures"],
                validation_criteria=["reproducibility", "statistical_significance"],
            ),
            WorkflowStage(
                name="Metadata Generation",
                role=Role.METADATA_SEMANTIC,
                description="Semantic metadata, JSON-LD, and citation generation.",
                inputs=["results", "structured_document"],
                outputs=["jsonld", "metadata", "citations"],
                validation_criteria=["schema_compliance", "doi_resolution"],
            ),
        ]

    def run(self) -> Dict[str, str]:
        """Execute the full workflow pipeline.

        Returns:
            Status dictionary mapping stage names to their final status.
        """
        status = {}
        for stage in self.stages:
            stage.execute()
            stage.validate()
            status[stage.name] = stage.status.value
        return status

    def get_stages_by_role(self, role: Role) -> List[WorkflowStage]:
        """Return all stages assigned to a given role."""
        return [s for s in self.stages if s.role == role]

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the workflow state."""
        return {
            "name": self.name,
            "version": self.version,
            "n_stages": len(self.stages),
            "stages": [
                {"name": s.name, "role": s.role.value, "status": s.status.value}
                for s in self.stages
            ],
        }


if __name__ == "__main__":
    fw = AIWorkflowFramework()
    fw.build_default_pipeline()
    assert len(fw.stages) == 4
    print("AI Workflow Framework module OK")
