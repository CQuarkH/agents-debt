from typing import Dict, Any
from .base import SteeringPolicy
from .constraints import derive_structural_boundaries

class ContextDebtPolicy(SteeringPolicy):
    """
    Steering Policy for Context Debt.
    
    Philosophy:
    Context debt is the discrepancy between what is claimed (Intent)
    and what is structurally possible (Domain Model).
    """

    def compute_constraints(self, domain_model: Dict[str, Any]) -> str:
        # We delegate to constraints.py the extraction of truth
        return derive_structural_boundaries(domain_model)

    def assemble_prompt(self, domain_model: Dict[str, Any], intent_context: str) -> str:
        # 1. Get the rigid boundaries
        structural_constraints = self.compute_constraints(domain_model)

        # 2. Define the interpretation policy (System Instructions)
        return f"""
Act as a Structural Consistency Auditor.

OBJECTIVE: Detect "Context Debt Smells" by validating the DECLARED INTENT against the STRUCTURAL BOUNDARIES.

INPUT DATA:
1. [INTENT] Declarative documentation (agents.md): 
   Represents what humans *claim* exists.

2. [REALITY] Structural Boundaries (Derived from cicd://model):
   Represents the ONLY entities that *actually* exist.
   {structural_constraints}

ANALYSIS POLICY (STRICT):
1. GROUNDING: You cannot assume the existence of any workflow, job, or step that is not explicitly defined in the Structural Boundaries.
2. VERIFIABILITY: If the Intent mentions a workflow "X" and "X" is not in the Boundaries -> This is a Context Debt Smell (Hallucinated Entity).
3. OBSOLESCENCE: If the Intent claims to use Action "v1" but the Boundary shows "v2" -> This is a Context Debt Smell (Drift).

OUTPUT FORMAT:
Generate a list of verifiable violations. Do not summarize the code. Only report discrepancies where the Intent violates the Structural Boundaries.

Format:
- [TYPE: Entity Mismatch | Version Drift | Logic Hallucination]
  - Claim: "Quote from agents.md"
  - Reality: "Reference to Structural Boundary"
  - Severity: High/Medium
""" + f"\n\n---\nDOCUMENTATION TO ANALYZE:\n{intent_context}"