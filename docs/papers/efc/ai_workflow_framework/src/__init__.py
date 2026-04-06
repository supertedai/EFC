"""
AI Workflow Framework module for Energy-Flow Cosmology.

Provides classes for modelling AI-augmented scientific workflows,
including role separation, validation pipelines, and metadata generation.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

from .ai_workflow import (
    AIWorkflowFramework,
    WorkflowStage,
    ValidationPipeline,
)

__all__ = [
    "AIWorkflowFramework",
    "WorkflowStage",
    "ValidationPipeline",
]
