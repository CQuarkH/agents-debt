"""
CAPABILITY: Workflow Files (Source Artifact)
Row: Workflow Files | Controlled By: Source Control

Provides access to raw workflow YAML files from the repository.
Uses a template pattern to access specific files by name.
"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP

def register_workflow_capabilities(mcp: FastMCP, repo_path: Path):
    """
    Registers workflow file access capabilities with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        repo_path: Path to the cloned repository
    """
    
    @mcp.resource("workflow://{filename}")
    def get_raw_workflow_file(filename: str) -> str:
        """
        Exposes the RAW content (original text) of a specific workflow file.
        Fulfills the 'Source Artifact' capability of the architecture.
        
        Security: Prevents Path Traversal attacks by validating file location.
        """
        workflows_dir = repo_path / ".github" / "workflows"
        target_file = (workflows_dir / filename).resolve()
        
        # Verify that the requested file is actually inside the workflows folder
        if not str(target_file).startswith(str(workflows_dir.resolve())):
            return "Error: Access denied. You can only read workflow files."
        
        if target_file.exists() and target_file.is_file():
            return target_file.read_text(encoding="utf-8")
        
        return f"Error: Workflow file '{filename}' not found."