#!/usr/bin/env python3
"""
Demo script to test the GitHub Onboarding MCP Server

This script demonstrates how to use the MCP server tools directly
without needing Codex or MCP Inspector.
"""

import asyncio
import json
from github_onboarding_mcp import (
    analyze_repository,
    get_setup_commands,
    identify_danger_zones,
    AnalyzeRepoInput,
    GetSetupCommandsInput,
    IdentifyDangerZonesInput,
    ResponseFormat
)


async def demo_analyze_repository() -> bool:
    """Demo: Analyze a complete repository."""
    print("=" * 80)
    print("DEMO 1: Analyze Complete Repository (facebook/react)")
    print("=" * 80)
    
    result = await analyze_repository(AnalyzeRepoInput(
        owner="facebook",
        repo="react",
        branch="main",
        response_format=ResponseFormat.MARKDOWN
    ))
    
    print(result)
    print("\n")
    return not result.startswith("Error:")


async def demo_get_setup_commands() -> bool:
    """Demo: Extract setup commands only."""
    print("=" * 80)
    print("DEMO 2: Get Setup Commands (vercel/next.js)")
    print("=" * 80)
    
    result = await get_setup_commands(GetSetupCommandsInput(
        owner="vercel",
        repo="next.js",
        branch="canary",
        response_format=ResponseFormat.JSON
    ))
    
    if not result or result.startswith("Error:"):
        print(result or "Error: No response received from server.")
        return False
    else:
        try:
            # Pretty print JSON
            data = json.loads(result)
            print(json.dumps(data, indent=2))
            print("\n")
            return True
        except json.JSONDecodeError:
            print("Error: Received a non-JSON response from server.")
            print(result)
            print("\n")
            return False


async def demo_identify_danger_zones() -> bool:
    """Demo: Identify risky code areas."""
    print("=" * 80)
    print("DEMO 3: Identify Danger Zones (example repo)")
    print("=" * 80)
    
    # Using a repo likely to have auth/security code
    result = await identify_danger_zones(IdentifyDangerZonesInput(
        owner="facebook",
        repo="react",
        branch="main",
        response_format=ResponseFormat.MARKDOWN
    ))
    
    print(result)
    print("\n")
    return not result.startswith("Error:")


async def demo_json_output() -> bool:
    """Demo: Get JSON output for programmatic use."""
    print("=" * 80)
    print("DEMO 4: JSON Output Format (psf/requests)")
    print("=" * 80)
    
    result = await analyze_repository(AnalyzeRepoInput(
        owner="psf",
        repo="requests",
        branch="main",
        response_format=ResponseFormat.JSON
    ))
    
    if not result or result.startswith("Error:"):
        print(result or "Error: No response received from server.")
        return False
    else:
        try:
            # Pretty print JSON
            data = json.loads(result)
            print(json.dumps(data, indent=2))
            print("\n")
            return True
        except json.JSONDecodeError:
            print("Error: Received a non-JSON response from server.")
            print(result)
            print("\n")
            return False


async def demo_error_handling() -> bool:
    """Demo: Error handling for non-existent repo."""
    print("=" * 80)
    print("DEMO 5: Error Handling (non-existent repo)")
    print("=" * 80)
    
    result = await analyze_repository(AnalyzeRepoInput(
        owner="nonexistent",
        repo="fakerepo12345",
        branch="main",
        response_format=ResponseFormat.MARKDOWN
    ))
    
    print(result)
    print("\n")
    return result.startswith("Error:")


async def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "GitHub Onboarding MCP Server Demo" + " " * 25 + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  This demo shows how the MCP server analyzes GitHub repositories" + " " * 10 + "║")
    print("║" + "  and generates onboarding guides for new developers." + " " * 21 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    try:
        # Run demos sequentially
        results = [
            await demo_analyze_repository(),
            await demo_get_setup_commands(),
            await demo_identify_danger_zones(),
            await demo_json_output(),
            await demo_error_handling(),
        ]
        
        print("=" * 80)
        print("DEMO COMPLETE!")
        print("=" * 80)
        print("\nAll demos executed successfully.")
        if all(results):
            print("The MCP server is working correctly and ready for use with Codex!")
        else:
            print("One or more demos reported errors. Check your network access and GitHub API connectivity.")
        print("\nNext steps:")
        print("1. Configure Codex to use this MCP server")
        print("2. Test with: codex chat --mcp github-onboarding")
        print("3. Ask Codex to analyze any GitHub repository")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {type(e).__name__}: {str(e)}")
        print("\nPlease ensure:")
        print("- You have internet connection (GitHub API access)")
        print("- Dependencies are installed: pip install -r requirements.txt")
        print("- You're not rate-limited by GitHub API")


if __name__ == "__main__":
    asyncio.run(main())
