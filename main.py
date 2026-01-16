#!/usr/bin/env python3
"""
GitHub MCP Server
Provides GitHub API access via Model Context Protocol
"""

import base64
import logging
import os
from typing import List, Dict, Any

import aiohttp
import gradio as gr
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8003"))
SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "random")
GITHUB_API_BASE = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize MCP server with a descriptive name
mcp = FastMCP("GitHub Knowledge Vault MCP Server")

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
# MCP Tools Registration
# ============================================================================

@mcp.tool()
async def get_org_repos_tool(org: str) -> List[Dict[str, Any]]:
    """
    Fetch all repositories from a GitHub organization

    This tool uses the GitHub Search API to efficiently find repositories
    that have a /doc folder, falling back to checking each repo individually
    if the search API is unavailable.

    Args:
        org: GitHub organization name (e.g., "microsoft", "google")

    Returns:
        List of repository dictionaries with structure:
        [
            {
                "id": "123456",
                "name": "repo-name",
                "description": "Repository description",
                "url": "https://github.com/org/repo",
                "hasDocFolder": true
            },
            ...
        ]

    Example:
        repos = await get_org_repos("anthropics")
    """
    return await get_org_repos(org)


@mcp.tool()
async def get_repo_docs_tool(org: str, repo: str) -> List[Dict[str, Any]]:
    """
    Get all documentation files from a repository's /doc folder

    Args:
        org: GitHub organization name
        repo: Repository name
    """
    return await get_repo_docs(org, repo)


@mcp.tool()
async def get_file_content_tool(org: str, repo: str, path: str) -> Dict[str, Any]:
    """
    Fetch and decode content of a specific file from GitHub

    Args:
        org: GitHub organization name
        repo: Repository name
        path: File path within repository (e.g., "doc/README.md")
    """
    return await get_file_content(org, repo, path)


@mcp.tool()
async def search_documentation_tool(org: str, query: str) -> List[Dict[str, Any]]:
    """
    Search for documentation files across all repositories in an organization

    Uses GitHub Code Search API to find matching files in /doc folders

    Args:
        org: GitHub organization name
        query: Search query string (e.g., "authentication", "API", "tutorial")

    Returns:
        List of search result dictionaries:
        [
            {
                "name": "authentication.md",
                "path": "doc/authentication.md",
                "repository": "repo-name",
                "url": "https://github.com/org/repo/blob/main/doc/auth.md",
            },
            ...
        ]

    Example:
        results = await search_documentation("anthropics", "streaming")
    """
    return await search_documentation(org, query)


# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("documentation://{org}/{repo}")
async def documentation_resource(org: str, repo: str) -> str:
    """
    MCP Resource: List documentation files in a repository

    URI Pattern: documentation://organization-name/repository-name

    Example URIs:
        documentation://anthropics/anthropic-sdk-python
        documentation://openai/openai-python

    Args:
        org: Organization name from URI
        repo: Repository name from URI

    Returns:
        Formatted string listing all documentation files
    """
    docs = await get_repo_docs(org, repo)

    if not docs:
        return f"No documentation found in {org}/{repo}/doc folder"

    # Format as readable list
    lines = [
        f"Documentation in {org}/{repo}",
        "=" * 50,
        ""
    ]

    for doc in docs:
        lines.append(f"📄 {doc['name']}")
        lines.append(f"   Type: {doc['type']}")
        lines.append(f"   Size: {doc['size']:,} bytes")
        lines.append(f"   Path: {doc['path']}")
        lines.append("")

    lines.append(f"Total: {len(docs)} files")

    return "\n".join(lines)


@mcp.resource("content://{org}/{repo}/{path}")
async def content_resource(org: str, repo: str, path: str) -> str:
    """
    MCP Resource: Get content of a specific file

    URI Pattern: content://organization/repository/path

    Example URIs:
        content://anthropics/sdk/doc/README.md
        content://openai/openai-python/doc/api-reference.md

    Args:
        org: Organization name from URI
        repo: Repository name from URI
        path: File path within repository (e.g., "doc/README.md")

    Returns:
        File content as string
    """
    file_data = await get_file_content(org, repo, path)
    return file_data["content"]

# Create Gradio Interface
def create_gradio_interface():
    """Create Gradio interface to display MCP server information"""

    async def get_server_info():
        """Get server status and information"""
        # Get tools using await (Gradio supports async functions)
        tools_dict = await mcp.get_tools()
        tools_list = list(tools_dict.values())

        # Build tools information
        tools_info = f"## 🛠️ Available MCP Tools ({len(tools_list)})\n\n"
        for tool in tools_list:
            tools_info += f"### {tool.name}\n"
            tools_info += f"{tool.description or 'No description available'}\n\n"

            if hasattr(tool, 'parameters') and tool.parameters:
                if hasattr(tool.parameters, 'properties'):
                    params = list(tool.parameters.properties.keys())
                    tools_info += f"**Parameters:** {', '.join(f'`{p}`' for p in params)}\n\n"

        return tools_info

    async def check_mcp_status():
        """Check if MCP endpoint is responding"""
        try:
            # Try to get tools to verify MCP server is working
            tools_dict = await mcp.get_tools()
            tool_count = len(tools_dict)
            return f"✅ MCP Server is running and responding\n✅ {tool_count} tools available at `/mcp` endpoint"
        except Exception as e:
            return f"❌ MCP Server error: {str(e)}"

    with gr.Blocks(title="GitHub MCP Server") as demo:
        demo.theme = gr.themes.Soft()
        gr.Markdown(
            """
            # 🐙 GitHub MCP Server

            Model Context Protocol server for accessing GitHub documentation via API.
            """
        )

        with gr.Tab("📡 MCP Endpoint"):
            gr.Markdown(
                """
                ### Connection Information

                **Endpoint:** `/mcp`
                **Protocol:** MCP over HTTP (Streamable HTTP)
                **Status:** Active

                ### How to Connect

                **Claude Desktop (Pro/Max/Team):**
                1. Open Settings → Connectors → Add Custom Integration
                2. Enter this Space's URL + `/mcp`
                3. Example: `https://your-username-space-name.hf.space/mcp`

                **Claude Desktop (Free tier):**
                Use `mcp-remote` proxy in your `claude_desktop_config.json`:
                ```json
                {
                  "mcpServers": {
                    "github-docs-remote": {
                      "command": "npx",
                      "args": ["-y", "mcp-remote", "https://your-space-url.hf.space/mcp"]
                    }
                  }
                }
                ```
                """
            )

            status_btn = gr.Button("Check MCP Status", variant="primary")
            status_output = gr.Textbox(label="Status", interactive=False)
            status_btn.click(check_mcp_status, outputs=status_output)

        with gr.Tab("🛠️ Available Tools"):
            gr.Markdown("View all available MCP tools and their parameters.")

            tools_btn = gr.Button("Load Tools", variant="primary")
            tools_output = gr.Markdown()
            tools_btn.click(get_server_info, outputs=tools_output)

        with gr.Tab("📚 Resources"):
            gr.Markdown(
                """
                ### MCP Resources

                This server provides MCP resources for accessing documentation:

                - `documentation://{org}/{repo}` - List documentation files in a repository
                - `content://{org}/{repo}/{path}` - Get content of a specific file

                ### Supported File Types

                - Markdown (`.md`)
                - Mermaid diagrams (`.mmd`, `.mermaid`)
                - SVG images (`.svg`)
                - OpenAPI specs (`.yml`, `.yaml`, `.json`)
                - Postman collections (`.json`)
                """
            )

        with gr.Tab("ℹ️ About"):
            gr.Markdown(
                f"""
                ### Server Information

                **GitHub Token:** {'✅ Configured' if GITHUB_TOKEN else '❌ Not configured'}
                **Port:** {SERVER_PORT}
                **API Base:** {GITHUB_API_BASE}

                ### Links

                - [FastMCP Documentation](https://github.com/jlowin/fastmcp)
                - [MCP Protocol Specification](https://modelcontextprotocol.io)
                - [Source Code](https://github.com/SPerekrestova/GitHub_MCP_Server)
                """
            )

    return demo

# Add health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

# Create Gradio blocks
gradio_blocks = create_gradio_interface()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    #gradio_blocks.launch(share=True)
    mcp.run()
