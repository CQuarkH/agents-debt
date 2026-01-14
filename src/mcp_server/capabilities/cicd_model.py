"""
CAPABILITY: CI/CD Domain Model
Row: CI/CD Domain Model | Controlled By: Application

Provides the parsed and validated CI/CD workflow structure.
This represents the 'Observable Reality' of the system.
"""

from pathlib import Path
import yaml
from mcp.server.fastmcp import FastMCP
from domain_model import Repository, Workflow

def get_repo_model(repo_path: Path) -> Repository:
    """
    Helper function that builds the 'CI/CD Domain Model'.
    This represents the 'Observable Reality' of the system.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Repository domain model with all workflows
    """
    repo_data = Repository(name=repo_path.name)
    workflows_dir = repo_path / ".github" / "workflows"
    
    # Basic existence validation
    if not workflows_dir.exists():
        # Return an empty repo if there are no workflows, to avoid breaking the server
        return repo_data

    files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
                
            # Fix for YAML 1.1 (on=True) vs 1.2 (on="on") compatibility
            if isinstance(raw_data, dict) and True in raw_data:
                raw_data["on"] = raw_data.pop(True)
                
            # Pydantic validation
            workflow = Workflow.model_validate(raw_data)
            repo_data.workflows[file_path.name] = workflow
        except Exception as e:
            # In a real server, we would use logging.error
            print(f"⚠️ Error loading {file_path.name}: {e}")
    
    return repo_data

def register_cicd_capabilities(mcp: FastMCP, repo_path: Path):
    """
    Registers CI/CD domain model capabilities with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        repo_path: Path to the cloned repository
    """
    
    @mcp.resource("cicd://model")
    def get_cicd_model() -> str:
        """
        Exposes the parsed and validated workflow structure.
        The Client calls this resource to get the 'truth' about the code.
        """
        repo = get_repo_model(repo_path)
        return repo.model_dump_json(indent=2)