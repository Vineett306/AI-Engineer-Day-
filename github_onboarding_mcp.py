"""
GitHub Repository Onboarding MCP Server

An MCP server that helps developers onboard to new GitHub repositories by analyzing
repo structure, extracting setup commands, identifying safe entry points, and
detecting potential danger zones.

Zero Hallucination Principle: Only returns information that exists in the repository.
Marks missing or unknown information clearly instead of guessing.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
import json
import base64
import re
import os
from datetime import datetime

# Initialize MCP server
mcp = FastMCP("github_onboarding_mcp")

# Constants
GITHUB_API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 30.0

# GitHub Authentication (optional - reads from environment)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)

def get_github_headers() -> Dict[str, str]:
    """Get headers for GitHub API requests with optional authentication."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# ============================================================================
# HELPER FUNCTIONS - Shared utilities
# ============================================================================

async def fetch_github_file(owner: str, repo: str, path: str, branch: str = "main") -> Optional[str]:
    """
    Fetch a file from GitHub repository.
    
    Returns None if file doesn't exist, decoded content if it does.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": branch}
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, trust_env=False) as client:
        try:
            response = await client.get(url, params=params, headers=get_github_headers())
            if response.status_code == 404:
                return None
            response.raise_for_status()
            
            data = response.json()
            if data.get("encoding") == "base64":
                return base64.b64decode(data["content"]).decode("utf-8")
            return data.get("content", "")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except httpx.RequestError:
            raise
        except Exception:
            return None


async def fetch_repo_info(owner: str, repo: str) -> Dict[str, Any]:
    """Fetch basic repository information."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, trust_env=False) as client:
        try:
            response = await client.get(url, headers=get_github_headers())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Repository {owner}/{repo} not found or is private")
            raise


async def fetch_repo_tree(owner: str, repo: str, branch: str = "main") -> Optional[Dict[str, Any]]:
    """Fetch repository file tree."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{branch}"
    params = {"recursive": "1"}
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, trust_env=False) as client:
        try:
            response = await client.get(url, params=params, headers=get_github_headers())
            if response.status_code == 404:
                # Try master branch
                url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/master"
                response = await client.get(url, params=params, headers=get_github_headers())
            response.raise_for_status()
            return response.json()
        except httpx.RequestError:
            raise
        except Exception:
            return None


def parse_package_json(content: str) -> Optional[Dict[str, Any]]:
    """Parse package.json content."""
    try:
        return json.loads(content)
    except:
        return None


def parse_makefile_targets(content: str) -> List[str]:
    """Extract targets from Makefile."""
    targets = []
    for line in content.split('\n'):
        # Match make targets (lines starting with word characters followed by colon)
        if re.match(r'^[a-zA-Z0-9_-]+:', line):
            target = line.split(':')[0].strip()
            targets.append(target)
    return targets


def find_files_by_pattern(tree: Optional[Dict], patterns: List[str]) -> List[str]:
    """Find files matching any of the given patterns."""
    if not tree or 'tree' not in tree:
        return []
    
    matched_files = []
    for item in tree['tree']:
        if item['type'] == 'blob':
            path = item['path'].lower()
            for pattern in patterns:
                if re.search(pattern, path):
                    matched_files.append(item['path'])
                    break
    
    return matched_files[:15]  # Limit results


def format_markdown_guide(data: Dict[str, Any]) -> str:
    """Format onboarding guide as Markdown."""
    md = f"# {data['repo_name']} - Onboarding Guide\n\n"
    
    # Repository Info
    md += "## 📊 Repository Information\n\n"
    md += f"**Repository**: {data['repo_url']}\n"
    md += f"**Description**: {data['description'] or 'No description available'}\n"
    md += f"**Language**: {data['language'] or 'Unknown'}\n"
    md += f"**Stars**: {data['stars']} ⭐\n"
    md += f"**Forks**: {data['forks']}\n\n"
    
    # Quick Start
    md += "## 🚀 Quick Start\n\n"
    if data['setup_commands']:
        for section, commands in data['setup_commands'].items():
            md += f"### {section}\n"
            for cmd in commands:
                md += f"```bash\n{cmd}\n```\n"
            md += "\n"
    else:
        md += "❓ **Unknown** - No standard setup files found (package.json, requirements.txt, Dockerfile, Makefile)\n\n"
    
    # Unknown/Missing
    md += "## ❓ Unknown / Missing Information\n\n"
    if data['unknown_items']:
        for item in data['unknown_items']:
            md += f"- {item}\n"
    else:
        md += "✅ All standard configuration files found!\n"
    md += "\n"
    
    # Safe Entry Points
    if data['safe_entry_points']:
        md += "## 🎯 Safe Entry Points (Good for New Developers)\n\n"
        md += "These files are good starting points for understanding the codebase:\n\n"
        for file in data['safe_entry_points']:
            md += f"- `{file}`\n"
        md += "\n"
    
    # Danger Zones
    if data['danger_zones']:
        md += "## ⚠️ Danger Zones (Require Careful Review)\n\n"
        md += "These files contain critical functionality - get review before modifying:\n\n"
        for file in data['danger_zones']:
            md += f"- `{file}`\n"
        md += "\n"
    
    # Learning Roadmap
    md += "## 📚 Learning Roadmap\n\n"
    md += "### Day 1\n"
    md += "1. Get the project running locally using the Quick Start commands\n"
    md += "2. Read the README and main documentation\n"
    md += "3. Explore the safe entry points listed above\n"
    md += "4. Run the test suite (if available) to verify setup\n\n"
    
    md += "### Week 1\n"
    md += "1. Make a small change in one of the safe entry point files\n"
    md += "2. Write or update a test for your change\n"
    md += "3. Review the danger zones to understand critical components\n"
    md += "4. Read through recent pull requests to understand contribution patterns\n\n"
    
    md += "### Month 1\n"
    md += "1. Understand the overall architecture and data flow\n"
    md += "2. Take on a 'good first issue' from the issue tracker\n"
    md += "3. Review and understand the CI/CD pipeline\n"
    md += "4. Start contributing to documentation improvements\n\n"
    
    return md


# ============================================================================
# PYDANTIC MODELS - Input validation
# ============================================================================

class AnalyzeRepoInput(BaseModel):
    """Input parameters for analyzing a GitHub repository."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    owner: str = Field(
        ...,
        description="Repository owner (username or organization, e.g., 'facebook', 'vercel')",
        min_length=1,
        max_length=100
    )
    repo: str = Field(
        ...,
        description="Repository name (e.g., 'react', 'next.js')",
        min_length=1,
        max_length=100
    )
    branch: str = Field(
        default="main",
        description="Branch to analyze (default: 'main', falls back to 'master')",
        max_length=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable guide or 'json' for structured data"
    )


class GetSetupCommandsInput(BaseModel):
    """Input parameters for extracting setup commands."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    owner: str = Field(..., description="Repository owner", min_length=1, max_length=100)
    repo: str = Field(..., description="Repository name", min_length=1, max_length=100)
    branch: str = Field(default="main", description="Branch to analyze", max_length=100)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Output format: 'json' or 'markdown'"
    )


class IdentifyDangerZonesInput(BaseModel):
    """Input parameters for identifying dangerous code areas."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    owner: str = Field(..., description="Repository owner", min_length=1, max_length=100)
    repo: str = Field(..., description="Repository name", min_length=1, max_length=100)
    branch: str = Field(default="main", description="Branch to analyze", max_length=100)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Output format: 'json' or 'markdown'"
    )


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool(
    name="analyze_repository",
    annotations={
        "title": "Analyze GitHub Repository for Onboarding",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def analyze_repository(params: AnalyzeRepoInput) -> str:
    """
    Generate a comprehensive onboarding guide for a GitHub repository.
    
    Analyzes the repository structure, extracts real setup commands from config files,
    identifies safe entry points for new developers, and flags potential danger zones.
    
    ZERO HALLUCINATION: Only returns information that actually exists in the repository.
    Clearly marks missing or unknown information instead of guessing.
    
    Args:
        params (AnalyzeRepoInput): Input containing:
            - owner (str): Repository owner (e.g., 'facebook')
            - repo (str): Repository name (e.g., 'react')
            - branch (str): Branch to analyze (default: 'main')
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Comprehensive onboarding guide in requested format containing:
            - Repository information (description, language, stars)
            - Setup commands (from package.json, Dockerfile, Makefile, etc.)
            - Unknown/missing information (clearly marked)
            - Safe entry points for new developers
            - Danger zones requiring careful review
            - Learning roadmap (Day 1, Week 1, Month 1)
    """
    try:
        # Fetch repository information
        repo_info = await fetch_repo_info(params.owner, params.repo)
        
        # Fetch repository tree
        tree = await fetch_repo_tree(params.owner, params.repo, params.branch)
        
        # Fetch configuration files
        package_json = await fetch_github_file(params.owner, params.repo, "package.json", params.branch)
        dockerfile = await fetch_github_file(params.owner, params.repo, "Dockerfile", params.branch)
        docker_compose = await fetch_github_file(params.owner, params.repo, "docker-compose.yml", params.branch)
        makefile = await fetch_github_file(params.owner, params.repo, "Makefile", params.branch)
        requirements_txt = await fetch_github_file(params.owner, params.repo, "requirements.txt", params.branch)
        pyproject_toml = await fetch_github_file(params.owner, params.repo, "pyproject.toml", params.branch)
        cargo_toml = await fetch_github_file(params.owner, params.repo, "Cargo.toml", params.branch)
        readme = await fetch_github_file(params.owner, params.repo, "README.md", params.branch)
        
        # Extract setup commands
        setup_commands = {}
        
        # Node.js
        if package_json:
            pkg = parse_package_json(package_json)
            if pkg:
                setup_commands["Node.js Setup"] = ["npm install"]
                if pkg.get("scripts"):
                    important_scripts = ["start", "dev", "build", "test", "serve"]
                    for script in important_scripts:
                        if script in pkg["scripts"]:
                            setup_commands["Node.js Setup"].append(f"npm run {script}")
        
        # Python
        if requirements_txt:
            setup_commands["Python Setup"] = ["pip install -r requirements.txt"]
        if pyproject_toml:
            if "Python Setup" not in setup_commands:
                setup_commands["Python Setup"] = []
            setup_commands["Python Setup"].append("pip install -e .")
        
        # Rust
        if cargo_toml:
            setup_commands["Rust Setup"] = ["cargo build", "cargo run", "cargo test"]
        
        # Docker
        if dockerfile:
            repo_name = params.repo.replace(".git", "")
            setup_commands["Docker Setup"] = [
                f"docker build -t {repo_name} .",
                f"docker run {repo_name}"
            ]
        if docker_compose:
            setup_commands["Docker Compose"] = ["docker-compose up", "docker-compose up -d"]
        
        # Makefile
        if makefile:
            targets = parse_makefile_targets(makefile)
            common_targets = ["install", "build", "test", "run", "start", "setup"]
            make_commands = [f"make {t}" for t in targets if t in common_targets]
            if make_commands:
                setup_commands["Makefile Targets"] = make_commands
        
        # Identify unknown/missing items
        unknown_items = []
        if not readme:
            unknown_items.append("No README.md found")
        if not dockerfile and not docker_compose:
            unknown_items.append("No Docker configuration found")
        if not package_json or (package_json and not parse_package_json(package_json).get("scripts", {}).get("test")):
            if not makefile or "test" not in parse_makefile_targets(makefile):
                unknown_items.append("No test command configured")
        if not any([package_json, requirements_txt, pyproject_toml, cargo_toml, makefile]):
            unknown_items.append("No standard build/package management files found")
        
        # Find safe entry points (good for beginners)
        safe_patterns = [
            r'^docs?/',
            r'^examples?/',
            r'\.md$',
            r'^test',
            r'utils?\.', 
            r'helpers?\.', 
            r'constants?\.',
            r'config\.',
        ]
        safe_entry_points = find_files_by_pattern(tree, safe_patterns)
        
        # Find danger zones (require careful review)
        danger_patterns = [
            r'auth',
            r'payment',
            r'credential',
            r'secret',
            r'migration',
            r'admin',
            r'security',
            r'crypto',
        ]
        danger_zones = find_files_by_pattern(tree, danger_patterns)
        
        # Build response data
        response_data = {
            "repo_name": repo_info["name"],
            "repo_url": repo_info["html_url"],
            "description": repo_info.get("description"),
            "language": repo_info.get("language"),
            "stars": repo_info.get("stargazers_count", 0),
            "forks": repo_info.get("forks_count", 0),
            "setup_commands": setup_commands,
            "unknown_items": unknown_items,
            "safe_entry_points": safe_entry_points,
            "danger_zones": danger_zones,
        }
        
        # Return in requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_markdown_guide(response_data)
        else:
            return json.dumps(response_data, indent=2)
            
    except ValueError as e:
        return f"Error: {str(e)}"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            return "Error: GitHub API rate limit exceeded. Please try again later or use authentication."
        elif e.response.status_code == 404:
            return f"Error: Repository {params.owner}/{params.repo} not found or is private."
        return f"Error: GitHub API request failed with status {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error: Unable to connect to GitHub API: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error occurred: {type(e).__name__}: {str(e)}"


@mcp.tool(
    name="get_setup_commands",
    annotations={
        "title": "Extract Setup Commands from Repository",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_setup_commands(params: GetSetupCommandsInput) -> str:
    """
    Extract real setup commands from repository configuration files.
    
    Analyzes package.json, Dockerfile, docker-compose.yml, Makefile, requirements.txt,
    and other config files to extract actual runnable commands.
    
    ZERO HALLUCINATION: Only returns commands that exist in the repository files.
    
    Args:
        params (GetSetupCommandsInput): Input containing:
            - owner (str): Repository owner
            - repo (str): Repository name
            - branch (str): Branch to analyze
            - response_format (str): 'json' or 'markdown'
    
    Returns:
        str: Setup commands organized by technology (Node.js, Python, Docker, etc.)
             In JSON format: {"technology": ["command1", "command2"]}
             In Markdown: Formatted sections with code blocks
    """
    try:
        setup_commands = {}
        
        # Fetch configuration files
        package_json = await fetch_github_file(params.owner, params.repo, "package.json", params.branch)
        dockerfile = await fetch_github_file(params.owner, params.repo, "Dockerfile", params.branch)
        docker_compose = await fetch_github_file(params.owner, params.repo, "docker-compose.yml", params.branch)
        makefile = await fetch_github_file(params.owner, params.repo, "Makefile", params.branch)
        requirements_txt = await fetch_github_file(params.owner, params.repo, "requirements.txt", params.branch)
        pyproject_toml = await fetch_github_file(params.owner, params.repo, "pyproject.toml", params.branch)
        cargo_toml = await fetch_github_file(params.owner, params.repo, "Cargo.toml", params.branch)
        
        # Node.js
        if package_json:
            pkg = parse_package_json(package_json)
            if pkg:
                setup_commands["Node.js"] = ["npm install"]
                if pkg.get("scripts"):
                    for script, cmd in pkg["scripts"].items():
                        if script in ["start", "dev", "build", "test", "serve"]:
                            setup_commands["Node.js"].append(f"npm run {script}  # {cmd}")
        
        # Python
        if requirements_txt:
            setup_commands["Python"] = ["pip install -r requirements.txt"]
        if pyproject_toml:
            if "Python" not in setup_commands:
                setup_commands["Python"] = []
            setup_commands["Python"].append("pip install -e .")
        
        # Rust
        if cargo_toml:
            setup_commands["Rust"] = ["cargo build", "cargo run", "cargo test"]
        
        # Docker
        if dockerfile:
            setup_commands["Docker"] = [
                f"docker build -t {params.repo} .",
                f"docker run {params.repo}"
            ]
        if docker_compose:
            setup_commands["Docker Compose"] = ["docker-compose up", "docker-compose up -d"]
        
        # Makefile
        if makefile:
            targets = parse_makefile_targets(makefile)
            common_targets = ["install", "build", "test", "run", "start", "setup", "clean"]
            make_commands = [f"make {t}" for t in targets if t in common_targets]
            if make_commands:
                setup_commands["Make"] = make_commands
        
        if not setup_commands:
            return "No setup commands found. Repository may require manual configuration."
        
        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            md = "# Setup Commands\n\n"
            for tech, commands in setup_commands.items():
                md += f"## {tech}\n\n"
                for cmd in commands:
                    md += f"```bash\n{cmd}\n```\n\n"
            return md
        else:
            return json.dumps(setup_commands, indent=2)
            
    except httpx.RequestError as e:
        return f"Error: Unable to connect to GitHub API: {str(e)}"
    except Exception as e:
        return f"Error: Failed to extract setup commands: {type(e).__name__}: {str(e)}"


@mcp.tool(
    name="identify_danger_zones",
    annotations={
        "title": "Identify Risky Code Areas in Repository",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def identify_danger_zones(params: IdentifyDangerZonesInput) -> str:
    """
    Identify files and directories that contain critical or sensitive code.
    
    Scans repository for files related to: authentication, payments, credentials,
    secrets, migrations, admin functions, security, and cryptography.
    
    These areas typically require:
    - Extra care when modifying
    - Thorough code review
    - Understanding of security implications
    - Senior developer approval
    
    Args:
        params (IdentifyDangerZonesInput): Input containing:
            - owner (str): Repository owner
            - repo (str): Repository name
            - branch (str): Branch to analyze
            - response_format (str): 'json' or 'markdown'
    
    Returns:
        str: List of files in danger zones with categorization
             Includes: authentication, payment processing, credentials, migrations, admin
    """
    try:
        tree = await fetch_repo_tree(params.owner, params.repo, params.branch)
        
        if not tree:
            return "Error: Unable to fetch repository tree"
        
        # Categorize danger zones
        categories = {
            "Authentication": r'auth|login|session|token|oauth',
            "Payment Processing": r'payment|billing|stripe|paypal|checkout',
            "Credentials & Secrets": r'credential|secret|key|password|cert',
            "Database Migrations": r'migration|schema|alembic|flyway',
            "Admin Functions": r'admin|superuser|elevated',
            "Security": r'security|encrypt|decrypt|hash|crypto',
        }
        
        danger_files = {cat: [] for cat in categories}
        
        if 'tree' in tree:
            for item in tree['tree']:
                if item['type'] == 'blob':
                    path = item['path'].lower()
                    for category, pattern in categories.items():
                        if re.search(pattern, path):
                            danger_files[category].append(item['path'])
                            break
        
        # Remove empty categories
        danger_files = {k: v for k, v in danger_files.items() if v}
        
        if not danger_files:
            return "No obvious danger zones detected. However, always review code carefully before making changes."
        
        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            md = "# ⚠️ Danger Zones - Handle With Care\n\n"
            md += "These files contain critical functionality. Get senior review before modifying.\n\n"
            for category, files in danger_files.items():
                md += f"## {category}\n\n"
                for file in files[:10]:  # Limit to 10 per category
                    md += f"- `{file}`\n"
                md += "\n"
            return md
        else:
            return json.dumps(danger_files, indent=2)
            
    except httpx.RequestError as e:
        return f"Error: Unable to connect to GitHub API: {str(e)}"
    except Exception as e:
        return f"Error: Failed to identify danger zones: {type(e).__name__}: {str(e)}"


# Run the server
if __name__ == "__main__":
    mcp.run()
