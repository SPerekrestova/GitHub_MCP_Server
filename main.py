#!/usr/bin/env python3
"""
GitHub MCP Server
Provides GitHub API access via Model Context Protocol using Gradio
"""

import base64
import json
import logging
import os
from typing import List, Dict, Any

import aiohttp
import gradio as gr

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_BASE = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# API Constants
RESULTS_PER_PAGE = 100
SEARCH_RESULTS_LIMIT = 50


# ============================================================================
# Helper Functions
# ============================================================================

def create_headers() -> Dict[str, str]:
    """
    Create GitHub API request headers with authentication

    Returns:
        Dictionary of HTTP headers for GitHub API requests
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-MCP-Server/1.0"
    }

    # Add authorization if token is available
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    return headers


async def check_doc_folder(
    session: aiohttp.ClientSession,
    org: str,
    repo: str
) -> bool:
    """
    Check if a repository has a /doc folder

    Args:
        session: aiohttp ClientSession (reuse connection)
        org: Organization name
        repo: Repository name

    Returns:
        True if /doc folder exists, False otherwise
    """
    headers = create_headers()
    url = f"{GITHUB_API_BASE}/repos/{org}/{repo}/contents/doc"

    try:
        async with session.get(url, headers=headers) as response:
            return response.status == 200
    except Exception as e:
        logger.debug(f"Error checking /doc folder for {org}/{repo}: {e}")
        return False


def determine_content_type(filename: str) -> str:
    """
    Determine content type from filename

    Args:
        filename: Name of the file

    Returns:
        Content type: 'markdown', 'mermaid', 'svg', 'openapi', 'postman', or 'unknown'
    """
    lower_name = filename.lower()

    if lower_name.endswith(('.mmd', '.mermaid')):
        return 'mermaid'
    elif lower_name.endswith('.md'):
        return 'markdown'
    elif lower_name.endswith('.svg'):
        return 'svg'
    elif lower_name.endswith(('.yml', '.yaml')):
        return 'openapi'
    elif lower_name.endswith('.json'):
        # Check if it's a Postman collection first, otherwise assume OpenAPI
        return 'postman' if lower_name.startswith('postman') else 'openapi'
    else:
        return 'unknown'


# ============================================================================
# Business Logic Functions (testable)
# ============================================================================

async def get_org_repos(org: str) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        headers = create_headers()

        # Strategy 1: Use GitHub Search API (efficient - one request)
        search_url = f"{GITHUB_API_BASE}/search/code"
        params = {
            "q": f"org:{org} path:/doc",
            "per_page": RESULTS_PER_PAGE
        }

        try:
            async with session.get(search_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    # Extract unique repositories from search results
                    repos_with_docs = {}
                    for item in data.get("items", []):
                        repo_info = item.get("repository", {})
                        repo_name = repo_info.get("name")

                        if repo_name and repo_name not in repos_with_docs:
                            repos_with_docs[repo_name] = {
                                "id": str(repo_info.get("id", "")),
                                "name": repo_name,
                                "description": repo_info.get("description") or "",
                                "url": repo_info.get("html_url", ""),
                                "hasDocFolder": True
                            }

                    logger.info(f"Found {len(repos_with_docs)} repos with /doc via search")
                    return list(repos_with_docs.values())

        except Exception as e:
            logger.warning(f"Search API failed: {e}, falling back to list all repos")

        # Strategy 2: Fallback - List all repos and check each one
        repos_url = f"{GITHUB_API_BASE}/orgs/{org}/repos"
        all_repos = []
        page = 1

        logger.info(f"Fetching repos for organization: {org}")

        while True:
            async with session.get(
                repos_url,
                headers=headers,
                params={"per_page": RESULTS_PER_PAGE, "page": page, "sort": "updated"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"GitHub API error {response.status}: {error_text}")

                repos = await response.json()
                if not repos:
                    break

                all_repos.extend(repos)
                logger.info(f"Fetched page {page} ({len(repos)} repos)")
                page += 1

                # Stop if we got less than full page (last page)
                if len(repos) < RESULTS_PER_PAGE:
                    break

        logger.info(f"Total repos fetched: {len(all_repos)}")

        # Check each repo for /doc folder
        result = []
        for idx, repo in enumerate(all_repos, 1):
            logger.info(f"Checking {idx}/{len(all_repos)}: {repo['name']}")
            has_doc = await check_doc_folder(session, org, repo["name"])

            result.append({
                "id": str(repo["id"]),
                "name": repo["name"],
                "description": repo.get("description") or "",
                "url": repo["html_url"],
                "hasDocFolder": has_doc
            })

        repos_with_docs_count = sum(1 for r in result if r["hasDocFolder"])
        logger.info(f"Found {repos_with_docs_count} repos with /doc folder")

        return result


async def get_repo_docs(org: str, repo: str) -> List[Dict[str, Any]]:
    """
    Get all documentation files from a repository's /doc folder

    Filters for supported file types: Markdown, Mermaid, SVG, OpenAPI, Postman

    Args:
        org: GitHub organization name
        repo: Repository name

    Returns:
        List of documentation file dictionaries:
        [
            {
                "id": "abc123...",
                "name": "README.md",
                "path": "doc/README.md",
                "type": "markdown",
                "url": "https://github.com/org/repo/blob/main/doc/README.md",
                "download_url": "https://raw.githubusercontent.com/.../README.md",
            },
            ...
        ]

    Example:
        docs = await get_repo_docs("anthropics", "anthropic-sdk-python")
    """
    async with aiohttp.ClientSession() as session:
        headers = create_headers()
        url = f"{GITHUB_API_BASE}/repos/{org}/{repo}/contents/doc"

        logger.info(f"Fetching docs from: {org}/{repo}/doc")

        async with session.get(url, headers=headers) as response:
            if response.status == 404:
                logger.warning(f"No /doc folder found in {org}/{repo}")
                return []

            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"GitHub API error {response.status}: {error_text}")

            contents = await response.json()

            # Filter for supported file types
            supported_extensions = [
                '.md',       # Markdown
                '.mmd',      # Mermaid
                '.mermaid',  # Mermaid
                '.svg',      # SVG images
                '.yml',      # YAML (OpenAPI)
                '.yaml',     # YAML (OpenAPI)
                '.json'      # JSON (OpenAPI/Postman)
            ]

            docs = []
            skipped = 0

            for item in contents:
                # Only process files (not directories)
                if item["type"] == "file":
                    name = item["name"]

                    # Check if file extension is supported
                    if any(name.lower().endswith(ext) for ext in supported_extensions):
                        content_type = determine_content_type(name)

                        docs.append({
                            "id": item["sha"],
                            "name": name,
                            "path": item["path"],
                            "type": content_type,
                            "url": item["html_url"],
                            "download_url": item.get("download_url", ""),
                        })
                    else:
                        skipped += 1

            logger.info(f"Found {len(docs)} documentation files ({skipped} skipped)")
            return docs


async def get_file_content(org: str, repo: str, path: str) -> Dict[str, Any]:
    """
    Fetch content of a specific file from GitHub

    Decodes base64-encoded content returned by GitHub API

    Args:
        org: GitHub organization name
        repo: Repository name
        path: File path within repository (e.g., "doc/README.md")

    Returns:
        Dictionary with file metadata and content:
        {
            "name": "README.md",
            "path": "doc/README.md",
            "content": "# Documentation\\n\\nThis is...",
            "encoding": "base64"
        }

    Example:
        content = await get_file_content("anthropics", "sdk", "doc/README.md")
    """
    async with aiohttp.ClientSession() as session:
        headers = create_headers()
        url = f"{GITHUB_API_BASE}/repos/{org}/{repo}/contents/{path}"

        logger.info(f"Fetching content: {org}/{repo}/{path}")

        async with session.get(url, headers=headers) as response:
            if response.status == 404:
                raise Exception(f"File not found: {path}")

            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"GitHub API error {response.status}: {error_text}")

            data = await response.json()

            # Decode base64 content if present
            content = ""
            if "content" in data and data["content"]:
                try:
                    # GitHub returns base64-encoded content with newlines
                    encoded_content = data["content"].replace('\n', '')
                    content = base64.b64decode(encoded_content).decode('utf-8')
                    logger.info(f"Decoded content ({len(content)} characters)")
                except Exception as e:
                    logger.warning(f"Failed to decode content: {e}")
                    content = data.get("content", "")

            return {
                "name": data["name"],
                "path": data["path"],
                "content": content,
                "encoding": data.get("encoding", "base64")
            }


async def search_documentation(org: str, query: str) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        headers = create_headers()
        search_url = f"{GITHUB_API_BASE}/search/code"
        params = {
            "q": f"org:{org} path:/doc {query}",
            "per_page": SEARCH_RESULTS_LIMIT
        }

        logger.info(f"Searching for: '{query}' in {org}")

        async with session.get(search_url, headers=headers, params=params) as response:
            if response.status == 403:
                raise Exception("Search API rate limit exceeded. Try again later.")

            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"GitHub API error {response.status}: {error_text}")

            data = await response.json()
            results = []

            for item in data.get("items", []):
                repo_info = item.get("repository", {})
                results.append({
                    "name": item["name"],
                    "path": item["path"],
                    "repository": repo_info.get("name", ""),
                    "url": item["html_url"],
                })

            logger.info(f"Found {len(results)} matching files")
            return results


# ============================================================================
# Gradio MCP Tool Functions
# ============================================================================

async def get_org_repos_tool(org: str) -> str:
    """
    Fetch all repositories from a GitHub organization with /doc folder detection.

    This tool uses the GitHub Search API to efficiently find repositories
    that have a /doc folder, falling back to checking each repo individually
    if the search API is unavailable.

    Args:
        org (str): GitHub organization name (e.g., "microsoft", "anthropics")

    Returns:
        str: JSON string containing list of repositories with their metadata
    """
    try:
        result = await get_org_repos(org)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_repo_docs_tool(org: str, repo: str) -> str:
    """
    Get all documentation files from a repository's /doc folder.

    Filters for supported file types: Markdown, Mermaid, SVG, OpenAPI, Postman.

    Args:
        org (str): GitHub organization name
        repo (str): Repository name

    Returns:
        str: JSON string containing list of documentation files with metadata
    """
    try:
        result = await get_repo_docs(org, repo)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_file_content_tool(org: str, repo: str, path: str) -> str:
    """
    Fetch and decode content of a specific file from GitHub.

    Automatically decodes base64-encoded content returned by GitHub API.

    Args:
        org (str): GitHub organization name
        repo (str): Repository name
        path (str): File path within repository (e.g., "doc/README.md")

    Returns:
        str: JSON string containing file metadata and decoded content
    """
    try:
        result = await get_file_content(org, repo, path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def search_documentation_tool(org: str, query: str) -> str:
    """
    Search for documentation files across all repositories in an organization.

    Uses GitHub Code Search API to find matching files in /doc folders.

    Args:
        org (str): GitHub organization name
        query (str): Search query string (e.g., "authentication", "API", "tutorial")

    Returns:
        str: JSON string containing list of matching files with their locations
    """
    try:
        result = await search_documentation(org, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# ============================================================================
# Gradio Interface
# ============================================================================

# Create individual interfaces for each tool
get_repos_interface = gr.Interface(
    fn=get_org_repos_tool,
    inputs=[gr.Textbox(label="Organization", placeholder="e.g., anthropics")],
    outputs=[gr.Textbox(label="Repositories (JSON)", lines=20)],
    title="Get Organization Repos",
    description="Fetch all repositories from a GitHub organization with /doc folder detection",
)

get_docs_interface = gr.Interface(
    fn=get_repo_docs_tool,
    inputs=[
        gr.Textbox(label="Organization", placeholder="e.g., anthropics"),
        gr.Textbox(label="Repository", placeholder="e.g., anthropic-sdk-python"),
    ],
    outputs=[gr.Textbox(label="Documentation Files (JSON)", lines=20)],
    title="Get Repository Docs",
    description="Get all documentation files from a repository's /doc folder",
)

get_content_interface = gr.Interface(
    fn=get_file_content_tool,
    inputs=[
        gr.Textbox(label="Organization", placeholder="e.g., anthropics"),
        gr.Textbox(label="Repository", placeholder="e.g., anthropic-sdk-python"),
        gr.Textbox(label="File Path", placeholder="e.g., doc/README.md"),
    ],
    outputs=[gr.Textbox(label="File Content (JSON)", lines=20)],
    title="Get File Content",
    description="Fetch and decode content of a specific file from GitHub",
)

search_docs_interface = gr.Interface(
    fn=search_documentation_tool,
    inputs=[
        gr.Textbox(label="Organization", placeholder="e.g., anthropics"),
        gr.Textbox(label="Search Query", placeholder="e.g., streaming"),
    ],
    outputs=[gr.Textbox(label="Search Results (JSON)", lines=20)],
    title="Search Documentation",
    description="Search for documentation files across all repositories in an organization",
)

# Combine into tabbed interface
demo = gr.TabbedInterface(
    [get_repos_interface, get_docs_interface, get_content_interface, search_docs_interface],
    ["Get Repos", "Get Docs", "Get Content", "Search"],
    title="GitHub MCP Server",
)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    demo.launch(mcp_server=True, server_name="0.0.0.0", server_port=7860)
