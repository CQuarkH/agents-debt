from pathlib import Path
import subprocess

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