from typing import Dict, Any, List

def derive_structural_boundaries(domain_model: Dict[str, Any]) -> str:
    """
    Analyzes the 'cicd://model' and generates an explicit list of existing entities.
    This converts the system's structure into the reasoning boundary.
    """
    boundaries = []
    boundaries.append("=== STRUCTURAL BOUNDARIES (SOURCE OF TRUTH) ===")
    
    # 1. Workflows Boundary
    workflows = domain_model.get("workflows", {})
    if not workflows:
        boundaries.append("RESTRICTION: No workflows exist in this repository.")
        return "\n".join(boundaries)

    boundaries.append(f"RESTRICTION: Only the following {len(workflows)} workflows exist:")
    
    for filename, wf_data in workflows.items():
        wf_name = wf_data.get("name", "Unnamed")
        boundaries.append(f"  - Workflow File: '{filename}' (ID: {wf_name})")
        
        # 2. Jobs Boundary
        jobs = wf_data.get("jobs", {})
        job_ids = list(jobs.keys())
        boundaries.append(f"    -> Allowed Jobs in '{filename}': {job_ids}")
        
        # 3. Steps/Actions Boundary (Optional deep dive)
        for j_id, j_data in jobs.items():
            steps = j_data.get("steps", [])
            uses = [s.get("uses") for s in steps if s.get("uses")]
            if uses:
                boundaries.append(f"       -> Valid Actions in '{j_id}': {uses}")

    boundaries.append("================================================")
    boundaries.append("RULE: Any assertion referencing a workflow, job, or action NOT listed above is FALSE.")
    
    return "\n".join(boundaries)