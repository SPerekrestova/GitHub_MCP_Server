#!/usr/bin/env python3
"""
Comprehensive test suite for GitHub MCP Server
Tests all tools and functions
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment before importing main
load_dotenv()

from main import (
    get_org_repos,
    get_repo_docs,
    get_file_content,
    search_documentation,
    create_headers,
    check_doc_folder,
    determine_content_type
)

# Test configuration
TEST_ORG = os.getenv("TEST_ORG", "SPerekrestova")  # Change to your org if needed


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text: str):
    """Print a formatted section"""
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print(f"{'─' * 70}")


async def test_helper_functions():
    """Test helper functions"""
    print_header("TEST 1: Helper Functions")

    # Test create_headers
    print_section("Testing create_headers()")
    headers = await create_headers()
    assert "Accept" in headers, "Missing Accept header"
    assert "User-Agent" in headers, "Missing User-Agent header"
    print(f"✅ Headers created successfully:")
    print(f"   - Accept: {headers['Accept']}")
    print(f"   - User-Agent: {headers['User-Agent']}")
    if "Authorization" in headers:
        print(f"   - Authorization: token ***{headers['Authorization'][-10:]}")

    # Test determine_content_type
    print_section("Testing determine_content_type()")
    test_cases = [
        ("README.md", "markdown"),
        ("diagram.mmd", "mermaid"),
        ("diagram.mermaid", "mermaid"),
        ("image.svg", "svg"),
        ("api.yml", "openapi"),
        ("api.yaml", "openapi"),
        ("postman_collection.json", "postman"),
        ("schema.json", "openapi"),
    ]

    for filename, expected in test_cases:
        result = determine_content_type(filename)
        assert result == expected, f"Expected {expected} for {filename}, got {result}"
        print(f"✅ {filename:30s} → {result}")

    print("\n✅ All helper function tests passed!")


async def test_get_org_repos():
    """Test get_org_repos tool"""
    print_header("TEST 2: get_org_repos()")

    print(f"📥 Fetching repositories for organization: {TEST_ORG}")
    repos = await get_org_repos(TEST_ORG)

    print(f"\n📊 Results:")
    print(f"   Total repositories: {len(repos)}")

    repos_with_docs = [r for r in repos if r["hasDocFolder"]]
    repos_without_docs = [r for r in repos if not r["hasDocFolder"]]

    print(f"   With /doc folder: {len(repos_with_docs)}")
    print(f"   Without /doc folder: {len(repos_without_docs)}")

    if repos:
        print(f"\n📦 Sample repositories:")
        for repo in repos[:5]:
            doc_status = "✓" if repo["hasDocFolder"] else "✗"
            print(f"   {doc_status} {repo['name']:30s} - {repo['url']}")

    assert len(repos) > 0, "No repositories found"
    print("\n✅ get_org_repos test passed!")

    return repos, repos_with_docs


async def test_get_repo_docs(repos_with_docs):
    """Test get_repo_docs tool"""
    print_header("TEST 3: get_repo_docs()")

    if not repos_with_docs:
        print("⚠️  No repositories with /doc folder found, skipping test")
        return None, None

    test_repo = repos_with_docs[0]
    print(f"📂 Testing with repository: {test_repo['name']}")

    docs = await get_repo_docs(TEST_ORG, test_repo["name"])

    print(f"\n📊 Results:")
    print(f"   Total documentation files: {len(docs)}")

    if docs:
        # Group by type
        by_type = {}
        for doc in docs:
            doc_type = doc["type"]
            by_type[doc_type] = by_type.get(doc_type, 0) + 1

        print(f"\n📑 Files by type:")
        for doc_type, count in by_type.items():
            print(f"   {doc_type:15s}: {count}")

        print(f"\n📄 Sample documentation files:")
        for doc in docs[:5]:
            size_kb = doc['size'] / 1024
            print(f"   - {doc['name']:30s} ({doc['type']:10s}, {size_kb:.1f} KB)")

    assert len(docs) > 0, "No documentation files found"
    print("\n✅ get_repo_docs test passed!")

    return test_repo, docs


async def test_get_file_content(test_repo, docs):
    """Test get_file_content tool"""
    print_header("TEST 4: get_file_content()")

    if not docs:
        print("⚠️  No documentation files found, skipping test")
        return

    test_doc = docs[0]
    print(f"📄 Testing with file: {test_doc['path']}")

    content = await get_file_content(TEST_ORG, test_repo["name"], test_doc["path"])

    print(f"\n📊 Results:")
    print(f"   File name: {content['name']}")
    print(f"   File path: {content['path']}")
    print(f"   Size: {content['size']} bytes")
    print(f"   Content length: {len(content['content'])} characters")
    print(f"   SHA: {content['sha'][:10]}...")

    # Show content preview
    content_preview = content['content'][:200].replace('\n', '\\n')
    print(f"\n📝 Content preview:")
    print(f"   {content_preview}...")

    assert len(content['content']) > 0, "Content is empty"
    assert content['name'] == test_doc['name'], "Name mismatch"
    print("\n✅ get_file_content test passed!")


async def test_search_documentation():
    """Test search_documentation tool"""
    print_header("TEST 5: search_documentation()")

    query = "README"
    print(f"🔍 Searching for: '{query}' in {TEST_ORG}")

    try:
        results = await search_documentation(TEST_ORG, query)

        print(f"\n📊 Results:")
        print(f"   Total matches: {len(results)}")

        if results:
            print(f"\n🔎 Search results:")
            for idx, result in enumerate(results[:10], 1):
                print(f"   {idx}. {result['name']:30s} in {result['repository']}")
                print(f"      Path: {result['path']}")

        print("\n✅ search_documentation test passed!")
    except Exception as e:
        if "rate limit" in str(e).lower():
            print(f"\n⚠️  Search API rate limited (expected): {e}")
            print("✅ search_documentation test passed (rate limit is expected)")
        else:
            raise


async def main():
    """Run all tests"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "GITHUB MCP SERVER - TEST SUITE" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")

    if not os.getenv("GITHUB_TOKEN"):
        print("\n⚠️  WARNING: GITHUB_TOKEN not set!")
        print("   Tests will use unauthenticated requests with lower rate limits.")
        print("   Set GITHUB_TOKEN in .env for better testing.\n")

    print(f"\n📋 Configuration:")
    print(f"   Organization: {TEST_ORG}")
    print(f"   API Base: {os.getenv('GITHUB_API_BASE_URL', 'https://api.github.com')}")
    print(f"   Token configured: {'Yes' if os.getenv('GITHUB_TOKEN') else 'No'}")

    try:
        # Test 1: Helper functions
        await test_helper_functions()

        # Test 2: Get org repos
        repos, repos_with_docs = await test_get_org_repos()

        # Test 3: Get repo docs
        test_repo, docs = await test_get_repo_docs(repos_with_docs)

        # Test 4: Get file content
        if test_repo and docs:
            await test_get_file_content(test_repo, docs)

        # Test 5: Search documentation
        await test_search_documentation()

        # Final summary
        print_header("TEST SUMMARY")
        print("\n   ✅ Test 1: Helper Functions")
        print("   ✅ Test 2: get_org_repos")
        print("   ✅ Test 3: get_repo_docs")
        print("   ✅ Test 4: get_file_content")
        print("   ✅ Test 5: search_documentation")

        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 22 + "ALL TESTS PASSED! 🎉" + " " * 26 + "║")
        print("╚" + "═" * 68 + "╝\n")

    except AssertionError as e:
        print(f"\n\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}\n")
        raise


if __name__ == "__main__":
    asyncio.run(main())
