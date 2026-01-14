"""
GitHub Actions Context Server - Entry Point

This server exposes GitHub Actions workflows and related documentation
through the Model Context Protocol (MCP).

Architecture:
- Capabilities are modular and self-contained
- Each capability is registered independently
- Easy to add new capabilities or clients
"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Import configuration
from config import REPO_URL, LOCAL_CLONE_PATH, FALLBACK_REPO_PATH, SERVER_NAME

# Import utilities
from utils.git_operations import clone_or_update_repo

# Import capability registration functions
from capabilities import (
    register_workflow_capabilities,
    register_cicd_capabilities,
    register_intent_capabilities
)

# Initialize MCP server
mcp = FastMCP(SERVER_NAME)

# Initialize repository path by cloning/updating from GitHub
try:
    REPO_PATH = clone_or_update_repo(REPO_URL, LOCAL_CLONE_PATH)
except Exception as e:
    print(f"⚠️ Warning: Could not clone repository. Using fallback path.")
    REPO_PATH = FALLBACK_REPO_PATH

# =============================================================================
# REGISTER ALL CAPABILITIES
# =============================================================================
register_workflow_capabilities(mcp, REPO_PATH)
register_cicd_capabilities(mcp, REPO_PATH)
register_intent_capabilities(mcp, REPO_PATH)

# =============================================================================
# MANAGEMENT TOOLS
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
        
        # Re-register capabilities with updated repo path
        # Note: This is a simplified approach. In production, you might want
        # a more sophisticated hot-reload mechanism
        
        return f"✅ Repository refreshed successfully at {REPO_PATH}"
    except Exception as e:
        return f"❌ Failed to refresh repository: {str(e)}"

@mcp.tool()
def list_capabilities() -> str:
    """
    Lists all available capabilities exposed by this server.
    Useful for discovery and documentation.
    """
    capabilities = """
📋 Available Capabilities:

1. **Workflow Files (Source Artifact)**
   - Resource: workflow://{filename}
   - Description: Access raw YAML workflow files
   - Example: workflow://ci.yml

2. **CI/CD Domain Model**
   - Resource: cicd://model
   - Description: Parsed and validated workflow structure
   - Returns: JSON representation of all workflows

3. **Project Intent Files**
   - Resource: intent://agents-md
   - Description: Human-written documentation and intent
   - Returns: Contents of agents.md file

🔧 Management Tools:
   - refresh_repository(): Update repo from GitHub
   - list_capabilities(): Show this help message
    """
    return capabilities

if __name__ == "__main__":
    mcp.run()