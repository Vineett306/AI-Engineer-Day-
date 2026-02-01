# 🚀 GitHub Repository Onboarding MCP Server

**Zero Hallucination • Real Commands Only • Instant Developer Onboarding**

An MCP (Model Context Protocol) server that enables Codex and other AI agents to analyze GitHub repositories and generate accurate onboarding guides for new developers.

Built for **Open AI Hackathon - Track 1: Agentic Software Engineering**

---

## 🎯 What It Does

This MCP server provides AI agents (like Codex) with tools to:

1. **Analyze any public GitHub repository** and generate comprehensive onboarding guides
2. **Extract real setup commands** from package.json, Dockerfile, Makefile, and other config files
3. **Identify safe entry points** for new developers (docs, tests, utilities)
4. **Flag danger zones** (authentication, payments, migrations, security code)
5. **Create learning roadmaps** (Day 1, Week 1, Month 1 guidance)

**Key Principle: ZERO HALLUCINATION**
- Only returns information that actually exists in the repository
- Clearly marks missing or unknown information
- Never guesses or invents commands

---

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

1. **Clone this repository**
```bash
git clone https://github.com/YOUR_USERNAME/github-onboarding-mcp.git
cd github-onboarding-mcp
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **[Optional] Set up GitHub Token** (Recommended to avoid rate limits)
```bash
# See GITHUB_TOKEN_SETUP.md for detailed instructions
export GITHUB_TOKEN="ghp_your_token_here"
```

Without a token, you're limited to 60 API requests/hour. With a token: 5,000/hour.

4. **Test the server**
```bash
python github_onboarding_mcp.py --help
```

---

## 🚀 How to Run

### Option 1: Use with Codex (Recommended for Hackathon)

1. **Start the MCP server**
```bash
python github_onboarding_mcp.py
```

2. **Configure Codex to use this MCP server**
Add to your Codex configuration (e.g., `~/.config/codex/config.json`):
```json
{
  "mcpServers": {
    "github-onboarding": {
      "command": "python",
      "args": ["/path/to/github_onboarding_mcp.py"]
    }
  }
}
```

3. **Use Codex to analyze repositories**
```bash
codex chat
> Analyze the facebook/react repository and create an onboarding guide
```

### Option 2: Standalone Testing

Run the server in stdio mode:
```bash
python github_onboarding_mcp.py
```

Then interact via MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python github_onboarding_mcp.py
```

---

## 📖 Available Tools

### 1. `analyze_repository`
Generate a complete onboarding guide for any GitHub repository.

**Input:**
- `owner`: Repository owner (e.g., "facebook")
- `repo`: Repository name (e.g., "react")
- `branch`: Branch to analyze (default: "main")
- `response_format`: "markdown" or "json"

**Example:**
```python
{
  "owner": "vercel",
  "repo": "next.js",
  "branch": "main",
  "response_format": "markdown"
}
```

**Output:** Complete onboarding guide with:
- Repository info (description, language, stars)
- Setup commands (from actual config files)
- Unknown/missing information (clearly marked)
- Safe entry points for beginners
- Danger zones requiring review
- Learning roadmap (Day 1, Week 1, Month 1)

---

### 2. `get_setup_commands`
Extract only the setup commands from repository configuration files.

**Input:**
- `owner`: Repository owner
- `repo`: Repository name
- `branch`: Branch to analyze
- `response_format`: "json" or "markdown"

**Example:**
```python
{
  "owner": "facebook",
  "repo": "react",
  "response_format": "json"
}
```

**Output:** Commands organized by technology:
```json
{
  "Node.js": [
    "npm install",
    "npm run build",
    "npm test"
  ],
  "Docker": [
    "docker build -t react .",
    "docker run react"
  ]
}
```

---

### 3. `identify_danger_zones`
Find files containing critical/sensitive code that requires extra care.

**Input:**
- `owner`: Repository owner
- `repo`: Repository name
- `branch`: Branch to analyze
- `response_format`: "json" or "markdown"

**Example:**
```python
{
  "owner": "stripe",
  "repo": "stripe-node",
  "response_format": "markdown"
}
```

**Output:** Categorized list of risky files:
- Authentication & Authorization
- Payment Processing
- Credentials & Secrets
- Database Migrations
- Admin Functions
- Security & Cryptography

---

## 🎥 Demo Steps

### Quick Demo with Codex

1. **Start Codex with the MCP server enabled**
```bash
codex chat --mcp github-onboarding
```

2. **Ask Codex to analyze a repository**
```
> Create an onboarding guide for the vercel/next.js repository
```

3. **Codex will use the MCP tools to:**
   - Fetch repository information
   - Extract setup commands from package.json
   - Identify safe entry points
   - Flag danger zones
   - Generate a complete markdown guide

4. **Save the guide**
```
> Save this guide to next-js-onboarding.md
```

### Testing Individual Tools

Use the MCP Inspector to test tools directly:

```bash
npx @modelcontextprotocol/inspector python github_onboarding_mcp.py
```

Then call tools from the inspector UI:
- Test `analyze_repository` with "facebook/react"
- Test `get_setup_commands` with "vercel/next.js"
- Test `identify_danger_zones` with different repos

---

## 💡 Why This Matters

### The Problem
**85% of developers waste 2+ hours** when joining a new codebase:
- READMEs are missing, outdated, or incomplete
- Setup instructions don't work or are unclear
- No guidance on where to start safely
- Fear of breaking critical code

### Our Solution
**5-minute onboarding instead of 5 hours:**
- Extract real, working commands from actual config files
- Clearly mark what's unknown instead of hallucinating
- Show safe starting points for new developers
- Flag critical code that needs careful review
- Provide structured learning roadmaps

### Impact Metrics
- **Time saved**: 2+ hours per developer per new repository
- **Reduced errors**: Clear danger zone identification prevents costly mistakes
- **Faster productivity**: New developers contribute on Day 1 instead of Week 1
- **Better code quality**: Guided approach leads to safer changes

---

## 🏗️ Technical Architecture

### MCP Server Design
- **Framework**: FastMCP (Python MCP SDK)
- **Transport**: stdio (for Codex integration)
- **API**: GitHub REST API (no authentication required for public repos)
- **Validation**: Pydantic v2 models for all inputs

### Zero Hallucination Implementation
1. **Direct file fetching**: Uses GitHub API to read actual files
2. **Pattern-based analysis**: Searches for known configuration patterns
3. **Explicit unknowns**: Returns "Unknown" when information is missing
4. **No inference**: Never guesses commands or configurations

### Tool Design Philosophy
- **Read-only operations**: All tools are safe and non-destructive
- **Idempotent**: Multiple calls produce same results
- **Composable**: Can be combined for complex workflows
- **Actionable errors**: Clear error messages guide users

---

## 🧪 Testing

### Unit Testing (Manual)
Test each tool individually:

```bash
# Test analyze_repository
python -c "
from github_onboarding_mcp import analyze_repository, AnalyzeRepoInput
import asyncio

async def test():
    result = await analyze_repository(AnalyzeRepoInput(
        owner='facebook',
        repo='react',
        response_format='markdown'
    ))
    print(result)

asyncio.run(test())
"
```

### Integration Testing
Use MCP Inspector to test the full server:
```bash
npx @modelcontextprotocol/inspector python github_onboarding_mcp.py
```

### Real-World Testing
Test with diverse repositories:
- **Large projects**: facebook/react, vercel/next.js
- **Python projects**: psf/requests, django/django
- **Docker-first**: docker/compose
- **Multiple languages**: rust-lang/rust
- **Minimal setup**: small personal repos

---

## 🚧 Known Limitations

1. **Public repositories only**: GitHub API requires authentication for private repos
2. **Rate limiting**: 60 requests/hour for unauthenticated API calls
3. **Branch availability**: Falls back to "master" if "main" doesn't exist
4. **Large repositories**: File tree limited to prevent timeouts
5. **Configuration detection**: Only recognizes standard file patterns

### Future Enhancements
- GitHub authentication support for private repos
- Caching to reduce API calls
- Support for more build systems (Gradle, Maven, Mix)
- Analysis of GitHub Actions workflows
- Team-specific onboarding templates
- Integration with issue trackers for "good first issue" identification

---

## 📊 Evaluation

This server includes 10 evaluation questions to test its effectiveness:

1. Find the setup command for a React repository
2. Identify danger zones in a payment processing repo
3. Extract Docker commands from a containerized app
4. Generate roadmap for a Python project
5. Detect missing documentation
6. Find safe entry points in a large codebase
7. Compare setup complexity across repositories
8. Identify repositories with good test coverage
9. Find migration files in database-heavy projects
10. Analyze multi-language repository setups

Run evaluations with:
```bash
python evaluation.py github_onboarding_mcp.py evaluations.xml
```

---

## 🤝 Contributing

This project was built for the OpenAI Hackathon 2026. Contributions are welcome!

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Ideas for Contributions
- Add support for more build systems
- Improve danger zone detection algorithms
- Add authentication for private repos
- Create web UI for non-Codex users
- Add multi-language support for output

---

## 📝 License

MIT License - Feel free to use and modify!

---

## 👥 Team

Built by Vineet Lal for OpenAI Hackathon 2026

**Track**: Agentic Software Engineering with Codex
**Focus**: Solving the "repo onboarding" pain point for developers

---

## 🙏 Acknowledgments

- OpenAI for Codex and the hackathon opportunity
- Anthropic for MCP specification and FastMCP framework
- GitHub for providing the REST API
- All open-source projects used in testing

---

## 📞 Support

Questions or issues? Open an issue on GitHub or contact 

---

**Built with ❤️ using Codex and MCP**
