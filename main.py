import os

import aiohttp
from fastmcp import FastMCP

mcp = FastMCP(name="GitHub Organization Repos Fetcher")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@mcp.tool
async def get_org_repos(org: str) -> list[dict]:
    """
    Fetch all public repos for the given GitHub organization.
    Returns a list of dicts with `name` and `url` keys.
    """
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        headers["Accept"] = "application/vnd.github.v3+json"

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
async def weather_resource(org: str, repo: str) -> str:
    """ Fetch /doc folder contents from a GitHub repository."""
    url = f"https://api.github.com/repos/{org}/{repo}/contents"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        headers["Accept"] = "application/vnd.github.v3+json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            # Check response status before returning
            response.raise_for_status()
            repos = await response.json()
    # Filter for 'doc' folder and return its contents
    docs = [item for item in repos if item["type"] == "dir" and item["name"] == "doc"]
    if not docs:
        return "No documentation folder found."
    doc_url = docs[0]["url"]
    async with aiohttp.ClientSession() as session:
        async with session.get(url=doc_url, headers=headers) as response:
            response.raise_for_status()
            doc_contents = await response.json()
    return [
        {"name": repo["name"], "url": repo["html_url"]}
        for repo in repos
    ]

if __name__ == "__main__":
    # By default, FastMCP will listen on localhost:8000
    mcp.run()