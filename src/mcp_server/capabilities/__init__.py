"""
Capabilities module for the GitHub Actions Context Server.

This module exposes the following capabilities:
1. Workflow Files (Source Artifact) - Raw workflow file access
2. CI/CD Domain Model - Parsed and validated workflow structure
3. Project Intent Files - Documentation and intent (agents.md)

Each capability is implemented in its own module for better maintainability.
"""

from .workflow_files import register_workflow_capabilities
from .cicd_model import register_cicd_capabilities
from .project_intent import register_intent_capabilities

__all__ = [
    'register_workflow_capabilities',
    'register_cicd_capabilities',
    'register_intent_capabilities'
]