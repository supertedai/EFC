"""EFC v2.1 Modular Synthesis -- modular decomposition of EFC.

Four independent modules: Structural, Dynamical, Entropic, Informational.
"""
from .efc_modular import (
    ModuleInterface, StructuralModule, DynamicalModule,
    EntropicModule, InformationalModule, ModularArchitecture,
)

__all__ = [
    "ModuleInterface", "StructuralModule", "DynamicalModule",
    "EntropicModule", "InformationalModule", "ModularArchitecture",
]
