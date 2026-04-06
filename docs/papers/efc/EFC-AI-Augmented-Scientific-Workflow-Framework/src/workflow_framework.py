"""AI-Augmented Scientific Workflow Framework -- core classes.

Models the structured workflow used in the EFC project: human-directed
reasoning with LLM assistance, validation gates, and reproducibility
metadata at every stage.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

from enum import Enum
from typing import Optional


class Role(Enum):
    """Role in the human-AI collaboration."""
    HUMAN = "human"
    AI = "ai"
    JOINT = "joint"


class WorkflowStage:
    """A single stage in the scientific workflow.

    Parameters
    ----------
    name : str
        Name of the stage (e.g., 'hypothesis', 'derivation', 'validation').
    role : Role
        Who leads this stage.
    description : str
        What happens at this stage.
    inputs : list of str
        Required inputs.
    outputs : list of str
        Expected outputs.
    """

    def __init__(self, name: str, role: Role, description: str,
                 inputs: Optional[list] = None,
                 outputs: Optional[list] = None):
        self.name = name
        self.role = role
        self.description = description
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.completed = False
        self.validation_passed = None

    def complete(self, passed: bool = True):
        """Mark this stage as completed."""
        self.completed = True
        self.validation_passed = passed

    def is_ready(self, available_inputs: list) -> bool:
        """Check if all required inputs are available."""
        return all(inp in available_inputs for inp in self.inputs)

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"WorkflowStage({self.name!r}, role={self.role.value}, {status})"


class ValidationLayer:
    """A validation gate in the workflow.

    Validation layers ensure that each stage produces outputs meeting
    defined criteria before the workflow can proceed.

    Parameters
    ----------
    name : str
        Validation layer name (e.g., 'EFC-D', 'EFC-S', 'EFC-C').
    criteria : list of str
        Criteria that must be met.
    """

    LAYERS = {
        "EFC-D": "Derivation validity -- equations are mathematically consistent",
        "EFC-S": "Statistical validity -- fits pass goodness-of-fit thresholds",
        "EFC-C": "Consistency -- results are consistent across independent probes",
    }

    def __init__(self, name: str, criteria: Optional[list] = None):
        self.name = name
        self.criteria = criteria or []
        self.results = {}

    def evaluate(self, criterion: str, passed: bool, notes: str = ""):
        """Record a criterion evaluation."""
        self.results[criterion] = {"passed": passed, "notes": notes}

    def all_passed(self) -> bool:
        """Check if all criteria pass."""
        if not self.results:
            return False
        return all(r["passed"] for r in self.results.values())

    def summary(self) -> dict:
        """Return a summary of the validation results."""
        return {
            "name": self.name,
            "description": self.LAYERS.get(self.name, ""),
            "criteria_count": len(self.criteria),
            "evaluated": len(self.results),
            "all_passed": self.all_passed(),
        }

    def __repr__(self) -> str:
        status = "PASS" if self.all_passed() else "PENDING"
        return f"ValidationLayer({self.name!r}, {status})"


class ScientificWorkflow:
    """The full AI-augmented scientific workflow.

    Manages stages, validation gates, and reproducibility metadata.

    Parameters
    ----------
    name : str
        Workflow name (e.g., a paper or analysis ID).
    author : str
        Lead author.
    """

    DEFAULT_STAGES = [
        ("hypothesis", Role.HUMAN, "Formulate the scientific hypothesis"),
        ("literature_review", Role.JOINT, "Survey existing work and identify gaps"),
        ("derivation", Role.JOINT, "Derive equations and theoretical results"),
        ("implementation", Role.AI, "Implement computational models"),
        ("validation", Role.JOINT, "Validate against data and consistency criteria"),
        ("documentation", Role.JOINT, "Write up results with full metadata"),
        ("peer_review", Role.HUMAN, "External review and revision"),
    ]

    def __init__(self, name: str, author: str = "Morten Magnusson"):
        self.name = name
        self.author = author
        self.stages = []
        self.validations = []
        self.metadata = {
            "name": name,
            "author": author,
            "reproducible": True,
        }

    def add_stage(self, stage: WorkflowStage):
        """Add a stage to the workflow."""
        self.stages.append(stage)

    def add_validation(self, layer: ValidationLayer):
        """Add a validation layer."""
        self.validations.append(layer)

    def build_default(self):
        """Build the default EFC workflow stages."""
        for name, role, desc in self.DEFAULT_STAGES:
            self.add_stage(WorkflowStage(name, role, desc))
        for layer_name in ValidationLayer.LAYERS:
            self.add_validation(ValidationLayer(layer_name))

    def completed_stages(self) -> list:
        """Return list of completed stage names."""
        return [s.name for s in self.stages if s.completed]

    def pending_stages(self) -> list:
        """Return list of pending stage names."""
        return [s.name for s in self.stages if not s.completed]

    def progress(self) -> float:
        """Return completion fraction (0.0 to 1.0)."""
        if not self.stages:
            return 0.0
        return len(self.completed_stages()) / len(self.stages)

    def summary(self) -> dict:
        """Return a full workflow summary."""
        return {
            "name": self.name,
            "author": self.author,
            "total_stages": len(self.stages),
            "completed": len(self.completed_stages()),
            "progress": f"{self.progress():.0%}",
            "validations": [v.summary() for v in self.validations],
        }

    def __repr__(self) -> str:
        return f"ScientificWorkflow({self.name!r}, {self.progress():.0%})"
