import os
from typing import Any

import aiohttp
from fastmcp import FastMCP

mcp = FastMCP(name="GitHub Organization Repos Fetcher")

@mcp.tool
async def get_org_repos(org: str) -> list[dict]:
    """
    Fetch all public repos for the given GitHub organization.
    Returns a list of dicts with `name` and `url` keys.
    """
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = await add_headers()

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            # Check response status before returning
            response.raise_for_status()
            repos =  await response.json()

    # Extract only name and HTML URL for each repo
    return [
        {"name": repo["name"], "url": repo["html_url"]}
        for repo in repos
    ]

@mcp.resource("documentation://{org_name}/{repo_name}")
async def documentation_resource(org_name: str, repo_name: str) -> list[dict[str, Any]] | str:
    """ Fetch /doc folder contents from a GitHub repository."""
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/doc"
    headers = await add_headers()

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            if response.status == 404:
                return "Documentation folder not found."
            response.raise_for_status()
            repo = await response.json()
    # Filter for 'doc' folder and return its contents
    docs = [item for item in repo if item["type"] == "file"]
    if not docs:
        return "Empty documentation folder"
    return [
        {"name": doc["name"]}
        for doc in docs
    ]


async def add_headers():
    headers = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        headers["Accept"] = "application/vnd.github.v3+json"
    return headers


if __name__ == "__main__":
    # By default, FastMCP will listen on localhost:8000
    mcp.run()