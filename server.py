from typing import List
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import yaml
import subprocess
import shutil
from domain.domain_model import Repository, Workflow

mcp = FastMCP("GitHub Actions Context Server")

# GitHub repository URL to clone
REPO_URL = "https://github.com/Rello/analytics.git"  # Change this to your target repo
LOCAL_CLONE_PATH = Path("./data/cloned-repos")  # Base directory for cloned repositories

def clone_or_update_repo(repo_url: str, target_path: Path) -> Path:
    """
    Clones a GitHub repository if it doesn't exist locally,
    or updates it if it already exists.
    
    Args:
        repo_url: GitHub repository URL (HTTPS)
        target_path: Local path where the repo will be cloned
    
    Returns:
        Path to the cloned repository
    """
    # Extract repo name from URL (e.g., "repo-name" from "https://github.com/user/repo-name.git")
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = target_path / repo_name
    
    try:
        if repo_path.exists():
            print(f"📂 Repository already exists at {repo_path}, updating...")
            # Pull latest changes
            subprocess.run(
                ["git", "-C", str(repo_path), "pull"],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ Repository updated successfully")
        else:
            print(f"📥 Cloning repository from {repo_url}...")
            # Create parent directory if it doesn't exist
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Clone the repository
            subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ Repository cloned successfully to {repo_path}")
        
        return repo_path
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e.stderr}")
        raise
    except Exception as e:
        print(f"❌ Error cloning/updating repository: {e}")
        raise

# Initialize repository path by cloning/updating from GitHub
try:
    REPO_PATH = clone_or_update_repo(REPO_URL, LOCAL_CLONE_PATH)
except Exception as e:
    print(f"⚠️ Warning: Could not clone repository. Using fallback path.")
    REPO_PATH = Path("./data/test-repo/analytics")

def get_repo_model() -> Repository:
    """
    Helper function that builds the 'CI/CD Domain Model' (Row 2 of the table).
    This represents the 'Observable Reality' of the system.
    """
    repo_data = Repository(name=REPO_PATH.name)
    workflows_dir = REPO_PATH / ".github" / "workflows"
    
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

# =============================================================================
# CAPABILITY: Workflow Files (Source Artifact)
# Note: We use a "Template" to access specific files by name.
# =============================================================================
@mcp.resource("workflow://{filename}")
def get_raw_workflow_file(filename: str) -> str:
    """
    Exposes the RAW content (original text) of a specific workflow file.
    Fulfills the 'Source Artifact' capability of the architecture.
    """
    # Basic security to prevent Path Traversal (reading files outside the folder)
    workflows_dir = REPO_PATH / ".github" / "workflows"
    target_file = (workflows_dir / filename).resolve()
    
    # Verify that the requested file is actually inside the workflows folder
    if not str(target_file).startswith(str(workflows_dir.resolve())):
        return "Error: Access denied. You can only read workflow files."
    
    if target_file.exists() and target_file.is_file():
        return target_file.read_text(encoding="utf-8")
    
    return f"Error: Workflow file '{filename}' not found."

# =============================================================================
# CAPABILITY: CI/CD Domain Model (Resource)
# Row: CI/CD Domain Model | Controlled By: Application
# =============================================================================
@mcp.resource("cicd://model")
def get_cicd_model() -> str:
    """
    Exposes the parsed and validated workflow structure.
    The Client calls this resource to get the 'truth' about the code.
    """
    repo = get_repo_model()
    return repo.model_dump_json(indent=2)

# =============================================================================
# CAPABILITY: Project Intent Files (Resource)
# Row: Project Intent Files (agents.md)
# =============================================================================
@mcp.resource("intent://agents-md")
def get_project_intent() -> str:
    """
    Exposes the declarative content of agents.md.
    The Client calls this resource to understand the human 'intention'.
    """
    # Standardize to the most common name in documentation: agents.md (plural or singular depending on your repo)
    possible_names = ["AGENTS.md", "agents.md", "AGENT.md", "agent.md"]
    
    for name in possible_names:
        agent_file = REPO_PATH / name
        if agent_file.exists():
            return agent_file.read_text(encoding="utf-8")
            
    return "Error: No agents.md file found in repository root."

# =============================================================================
# TOOL: Force Repository Refresh
# =============================================================================
@mcp.tool()
def refresh_repository() -> str:
    """
    Forces a fresh clone or pull of the repository from GitHub.
    Useful when you want to ensure you have the latest version.
    """
    global REPO_PATH
    try:
        REPO_PATH = clone_or_update_repo(REPO_URL, LOCAL_CLONE_PATH)
        return f"✅ Repository refreshed successfully at {REPO_PATH}"
    except Exception as e:
        return f"❌ Failed to refresh repository: {str(e)}"

if __name__ == "__main__":
    mcp.run()