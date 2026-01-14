from abc import ABC, abstractmethod
from typing import Dict, Any

class SteeringPolicy(ABC):
    """
    Defines the interface for an interpretation policy.
    A policy is not just a prompt, it's the logic that transforms
    MCP resources into a bounded and verifiable cognitive task.
    """

    @abstractmethod
    def compute_constraints(self, domain_model: Dict[str, Any]) -> str:
        """Derives the unbreakable rules from the model."""
        pass

    @abstractmethod
    def assemble_prompt(self, domain_model: Dict[str, Any], intent_context: str) -> str:
        """
        Composes the cognitive task by injecting the constraints.
        """
        pass