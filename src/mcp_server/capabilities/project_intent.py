"""
CAPABILITY: Project Intent Files
Row: Project Intent Files | Controlled By: Documentation

Provides access to human-written intent and documentation files (AGENTS.md files).
Primary focus: agents.md file that describes intended behavior.
"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP

def register_intent_capabilities(mcp: FastMCP, repo_path: Path):
    """
    Registers project intent file capabilities with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        repo_path: Path to the cloned repository
    """
    
    @mcp.resource("intent://agents-md")
    def get_project_intent() -> str:
        """
        Exposes the declarative content of agents.md.
        The Client calls this resource to understand the human 'intention'.
        
        Searches for common variants: AGENTS.md, agents.md, AGENT.md, agent.md
        """
        possible_names = ["AGENTS.md", "agents.md", "AGENT.md", "agent.md"]
        
        for name in possible_names:
            agent_file = repo_path / name
            if agent_file.exists():
                return agent_file.read_text(encoding="utf-8")
                
        return "Error: No agents.md file found in repository root."