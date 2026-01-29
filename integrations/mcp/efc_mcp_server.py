#!/usr/bin/env python3
"""
EFC MCP Server - Model Context Protocol server for Energy-Flow Cosmology

This server enables AI agents to manage EFC resources across multiple surfaces:
- Repository maintenance
- Website posting (energyflow-cosmology.com, magnusson.as)
- Figshare publication management
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

# MCP SDK imports (install with: pip install mcp)
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.types import Tool, TextContent, Resource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP SDK not installed. Install with: pip install mcp")

# Optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("efc-mcp")

# Configuration from environment
EFC_ROOT = Path(os.environ.get("EFC_ROOT", "."))
FIGSHARE_TOKEN = os.environ.get("FIGSHARE_TOKEN", "")
WP_EFC_URL = os.environ.get("WP_EFC_URL", "https://energyflow-cosmology.com/")
WP_EFC_USER = os.environ.get("WP_EFC_USER", "")
WP_EFC_APP_PASSWORD = os.environ.get("WP_EFC_APP_PASSWORD", "")
WP_MAGNUSSON_URL = os.environ.get("WP_MAGNUSSON_URL", "https://www.magnusson.as/")
WP_MAGNUSSON_USER = os.environ.get("WP_MAGNUSSON_USER", "")
WP_MAGNUSSON_APP_PASSWORD = os.environ.get("WP_MAGNUSSON_APP_PASSWORD", "")


class EFCMCPServer:
    """MCP Server for Energy-Flow Cosmology management."""

    def __init__(self):
        self.efc_root = EFC_ROOT
        self.server = Server("efc-mcp-server") if MCP_AVAILABLE else None

    # ==================== Repository Tools ====================

    def validate_jsonld(self, path: str = "/jsonld/", fix: bool = False) -> dict:
        """Validate JSON-LD files against schema."""
        results = {"valid": [], "invalid": [], "fixed": []}
        target_path = self.efc_root / path.lstrip("/")

        if not target_path.exists():
            return {"error": f"Path not found: {target_path}"}

        for jsonld_file in target_path.glob("**/*.jsonld"):
            try:
                with open(jsonld_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Basic validation
                if "@context" not in data:
                    results["invalid"].append({
                        "file": str(jsonld_file.relative_to(self.efc_root)),
                        "error": "Missing @context"
                    })
                    if fix:
                        data["@context"] = "https://schema.org"
                        with open(jsonld_file, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                        results["fixed"].append(str(jsonld_file.relative_to(self.efc_root)))
                else:
                    results["valid"].append(str(jsonld_file.relative_to(self.efc_root)))

            except json.JSONDecodeError as e:
                results["invalid"].append({
                    "file": str(jsonld_file.relative_to(self.efc_root)),
                    "error": f"Invalid JSON: {e}"
                })

        return results

    def update_doi_map(self) -> dict:
        """Update figshare/doi-map.json from Figshare API."""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests library not installed"}
        if not FIGSHARE_TOKEN:
            return {"error": "FIGSHARE_TOKEN not set"}

        headers = {"Authorization": f"token {FIGSHARE_TOKEN}"}
        response = requests.get(
            "https://api.figshare.com/v2/account/articles",
            headers=headers
        )

        if response.status_code != 200:
            return {"error": f"Figshare API error: {response.status_code}"}

        articles = response.json()
        doi_map = {}

        for article in articles:
            if article.get("doi"):
                doi_map[article["doi"]] = {
                    "id": article["id"],
                    "url": article["url_public_html"]
                }

        # Save to file
        doi_map_path = self.efc_root / "figshare" / "doi-map.json"
        with open(doi_map_path, "w", encoding="utf-8") as f:
            json.dump(doi_map, f, indent=2)

        return {"updated": len(doi_map), "path": str(doi_map_path)}

    def check_links(self, include_external: bool = False) -> dict:
        """Verify internal and external links."""
        results = {"internal": {"valid": 0, "broken": []}, "external": {"valid": 0, "broken": []}}

        # Check internal links in markdown files
        for md_file in self.efc_root.glob("**/*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple link extraction (could be more sophisticated)
            import re
            links = re.findall(r'\[.*?\]\((.*?)\)', content)

            for link in links:
                if link.startswith("http"):
                    if include_external and REQUESTS_AVAILABLE:
                        try:
                            resp = requests.head(link, timeout=5, allow_redirects=True)
                            if resp.status_code < 400:
                                results["external"]["valid"] += 1
                            else:
                                results["external"]["broken"].append({
                                    "file": str(md_file.relative_to(self.efc_root)),
                                    "link": link,
                                    "status": resp.status_code
                                })
                        except Exception as e:
                            results["external"]["broken"].append({
                                "file": str(md_file.relative_to(self.efc_root)),
                                "link": link,
                                "error": str(e)
                            })
                elif not link.startswith("#"):
                    # Internal link
                    target = md_file.parent / link
                    if target.exists():
                        results["internal"]["valid"] += 1
                    else:
                        results["internal"]["broken"].append({
                            "file": str(md_file.relative_to(self.efc_root)),
                            "link": link
                        })

        return results

    # ==================== WordPress Tools ====================

    def _get_wp_config(self, site: str) -> tuple:
        """Get WordPress configuration for a site."""
        if site == "efc":
            return WP_EFC_URL, WP_EFC_USER, WP_EFC_APP_PASSWORD
        elif site == "magnusson":
            return WP_MAGNUSSON_URL, WP_MAGNUSSON_USER, WP_MAGNUSSON_APP_PASSWORD
        else:
            raise ValueError(f"Unknown site: {site}")

    def wp_list_posts(self, site: str, status: str = "any", limit: int = 10) -> dict:
        """List posts from a WordPress site."""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests library not installed"}

        url, user, password = self._get_wp_config(site)
        if not all([url, user, password]):
            return {"error": f"WordPress credentials not configured for {site}"}

        endpoint = f"{url.rstrip('/')}/wp-json/wp/v2/posts"
        params = {"per_page": limit}
        if status != "any":
            params["status"] = status

        response = requests.get(endpoint, auth=(user, password), params=params)

        if response.status_code != 200:
            return {"error": f"WordPress API error: {response.status_code}"}

        posts = response.json()
        return {
            "site": site,
            "count": len(posts),
            "posts": [
                {
                    "id": p["id"],
                    "title": p["title"]["rendered"],
                    "status": p["status"],
                    "date": p["date"],
                    "link": p["link"]
                }
                for p in posts
            ]
        }

    def wp_create_post(
        self,
        site: str,
        title: str,
        content: str,
        status: str = "draft",
        categories: Optional[list] = None,
        tags: Optional[list] = None,
        meta: Optional[dict] = None
    ) -> dict:
        """Create a new WordPress post."""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests library not installed"}

        url, user, password = self._get_wp_config(site)
        if not all([url, user, password]):
            return {"error": f"WordPress credentials not configured for {site}"}

        endpoint = f"{url.rstrip('/')}/wp-json/wp/v2/posts"

        data = {
            "title": title,
            "content": content,
            "status": status
        }

        if categories:
            data["categories"] = categories
        if tags:
            data["tags"] = tags
        if meta:
            data["meta"] = meta

        response = requests.post(endpoint, auth=(user, password), json=data)

        if response.status_code not in [200, 201]:
            return {"error": f"WordPress API error: {response.status_code}", "details": response.text}

        post = response.json()
        return {
            "success": True,
            "id": post["id"],
            "link": post["link"],
            "status": post["status"]
        }

    # ==================== Figshare Tools ====================

    def figshare_list_articles(self, page: int = 1, page_size: int = 10) -> dict:
        """List Figshare articles."""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests library not installed"}
        if not FIGSHARE_TOKEN:
            return {"error": "FIGSHARE_TOKEN not set"}

        headers = {"Authorization": f"token {FIGSHARE_TOKEN}"}
        params = {"page": page, "page_size": page_size}

        response = requests.get(
            "https://api.figshare.com/v2/account/articles",
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            return {"error": f"Figshare API error: {response.status_code}"}

        return {"articles": response.json()}

    def figshare_create_article(
        self,
        title: str,
        description: str,
        keywords: Optional[list] = None,
        categories: Optional[list] = None,
        defined_type: str = "preprint",
        license_id: int = 1  # CC-BY
    ) -> dict:
        """Create a new Figshare article."""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests library not installed"}
        if not FIGSHARE_TOKEN:
            return {"error": "FIGSHARE_TOKEN not set"}

        headers = {"Authorization": f"token {FIGSHARE_TOKEN}"}

        data = {
            "title": title,
            "description": description,
            "defined_type": defined_type,
            "license": license_id,
            "authors": [{"name": "Morten Magnusson", "orcid_id": "0009-0002-4860-5095"}]
        }

        if keywords:
            data["keywords"] = keywords
        if categories:
            data["categories"] = categories

        response = requests.post(
            "https://api.figshare.com/v2/account/articles",
            headers=headers,
            json=data
        )

        if response.status_code not in [200, 201]:
            return {"error": f"Figshare API error: {response.status_code}", "details": response.text}

        return response.json()

    def figshare_publish(self, article_id: int) -> dict:
        """Publish a Figshare article (assigns DOI)."""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests library not installed"}
        if not FIGSHARE_TOKEN:
            return {"error": "FIGSHARE_TOKEN not set"}

        headers = {"Authorization": f"token {FIGSHARE_TOKEN}"}

        response = requests.post(
            f"https://api.figshare.com/v2/account/articles/{article_id}/publish",
            headers=headers
        )

        if response.status_code not in [200, 201]:
            return {"error": f"Figshare API error: {response.status_code}", "details": response.text}

        return {"success": True, "article_id": article_id}

    # ==================== Synchronization ====================

    def sync_metadata(self, dry_run: bool = True) -> dict:
        """Synchronize metadata across repository files."""
        changes = []

        # Load author info
        authors_path = self.efc_root / "schema" / "authors.json"
        if authors_path.exists():
            with open(authors_path, "r", encoding="utf-8") as f:
                authors = json.load(f)
        else:
            authors = {"authors": [{"name": "Morten Magnusson", "orcid": "https://orcid.org/0009-0002-4860-5095"}]}

        # Update all JSON-LD files with consistent author info
        for jsonld_file in self.efc_root.glob("**/*.jsonld"):
            try:
                with open(jsonld_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                modified = False

                # Ensure consistent author/creator
                if "creator" in data or "author" in data:
                    key = "creator" if "creator" in data else "author"
                    if isinstance(data[key], dict) and data[key].get("name") == "Morten Magnusson":
                        if data[key].get("sameAs") != "https://orcid.org/0009-0002-4860-5095":
                            changes.append({
                                "file": str(jsonld_file.relative_to(self.efc_root)),
                                "change": "Update ORCID link"
                            })
                            if not dry_run:
                                data[key]["sameAs"] = "https://orcid.org/0009-0002-4860-5095"
                                modified = True

                if modified:
                    with open(jsonld_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)

            except (json.JSONDecodeError, KeyError):
                continue

        return {"dry_run": dry_run, "changes": changes}

    def full_sync(self, dry_run: bool = True, surfaces: Optional[list] = None) -> dict:
        """Complete synchronization across all surfaces."""
        if surfaces is None:
            surfaces = ["repository", "figshare"]

        results = {"dry_run": dry_run, "surfaces": {}}

        if "repository" in surfaces:
            results["surfaces"]["repository"] = {
                "jsonld_validation": self.validate_jsonld(),
                "metadata_sync": self.sync_metadata(dry_run=dry_run)
            }

        if "figshare" in surfaces and FIGSHARE_TOKEN:
            results["surfaces"]["figshare"] = {
                "doi_map_update": self.update_doi_map() if not dry_run else {"status": "would update"}
            }

        # Log sync
        if not dry_run:
            sync_log_path = self.efc_root / "figshare" / "sync_log.json"
            if sync_log_path.exists():
                with open(sync_log_path, "r", encoding="utf-8") as f:
                    sync_log = json.load(f)
            else:
                sync_log = {"syncs": []}

            sync_log["syncs"].append({
                "timestamp": datetime.now().isoformat(),
                "surfaces": surfaces,
                "results": results
            })

            with open(sync_log_path, "w", encoding="utf-8") as f:
                json.dump(sync_log, f, indent=2)

        return results


def main():
    """Run the MCP server."""
    if not MCP_AVAILABLE:
        print("MCP SDK not available. Running in standalone mode.")
        server = EFCMCPServer()

        # Demo: validate JSON-LD
        print("\nValidating JSON-LD files...")
        result = server.validate_jsonld()
        print(f"Valid: {len(result.get('valid', []))}")
        print(f"Invalid: {len(result.get('invalid', []))}")

        return

    # Full MCP server implementation would go here
    # This requires the MCP SDK to be properly configured
    print("Starting EFC MCP Server...")
    server = EFCMCPServer()

    # Register tools, resources, and prompts with the MCP server
    # (Implementation depends on MCP SDK version)


if __name__ == "__main__":
    main()
