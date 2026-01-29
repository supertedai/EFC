# EFC MCP Server

Model Context Protocol (MCP) server for AI agent management of Energy-Flow Cosmology resources.

## Overview

This MCP server enables AI agents to:

1. **Website Management** - Post and update content on energyflow-cosmology.com and magnusson.as
2. **Figshare Integration** - Upload publications, update metadata, manage DOIs
3. **Repository Maintenance** - Validate JSON-LD, update semantic graphs, sync metadata
4. **Content Synchronization** - Keep all surfaces in sync

## Installation

### For Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "efc": {
      "command": "python",
      "args": ["-m", "efc_mcp_server"],
      "cwd": "/path/to/EFC/integrations/mcp",
      "env": {
        "EFC_ROOT": "/path/to/EFC",
        "FIGSHARE_TOKEN": "your-figshare-token",
        "WP_EFC_URL": "https://energyflow-cosmology.com/",
        "WP_EFC_USER": "your-username",
        "WP_EFC_APP_PASSWORD": "your-app-password",
        "WP_MAGNUSSON_URL": "https://www.magnusson.as/",
        "WP_MAGNUSSON_USER": "your-username",
        "WP_MAGNUSSON_APP_PASSWORD": "your-app-password"
      }
    }
  }
}
```

### For Claude Code CLI

```bash
export EFC_ROOT=/path/to/EFC
export FIGSHARE_TOKEN=your-figshare-token
# ... other env vars

cd /path/to/EFC/integrations/mcp
python -m efc_mcp_server
```

## Available Tools

### Website Tools

| Tool | Description |
|------|-------------|
| `wp_list_posts` | List posts from a WordPress site |
| `wp_create_post` | Create a new post |
| `wp_update_post` | Update an existing post |
| `wp_upload_media` | Upload media files |
| `wp_get_categories` | Get available categories |

### Figshare Tools

| Tool | Description |
|------|-------------|
| `figshare_list_articles` | List your Figshare articles |
| `figshare_create_article` | Create a new article |
| `figshare_update_article` | Update article metadata |
| `figshare_upload_file` | Upload a file to an article |
| `figshare_publish` | Publish a draft article |
| `figshare_get_doi` | Get DOI for an article |

### Repository Tools

| Tool | Description |
|------|-------------|
| `validate_jsonld` | Validate JSON-LD files against schema |
| `update_doi_map` | Update figshare/doi-map.json |
| `sync_metadata` | Synchronize metadata across files |
| `check_links` | Verify internal and external links |
| `generate_sitemap` | Update schema/site-graph.json |

### Synchronization Tools

| Tool | Description |
|------|-------------|
| `sync_to_website` | Push repository content to website |
| `sync_from_figshare` | Pull DOI updates from Figshare |
| `full_sync` | Complete synchronization across all surfaces |

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `EFC_ROOT` | Path to EFC repository root | Yes |
| `FIGSHARE_TOKEN` | Figshare API token | For Figshare |
| `WP_EFC_URL` | energyflow-cosmology.com URL | For EFC site |
| `WP_EFC_USER` | WordPress username | For EFC site |
| `WP_EFC_APP_PASSWORD` | WordPress app password | For EFC site |
| `WP_MAGNUSSON_URL` | magnusson.as URL | For personal site |
| `WP_MAGNUSSON_USER` | WordPress username | For personal site |
| `WP_MAGNUSSON_APP_PASSWORD` | WordPress app password | For personal site |

### Getting API Credentials

#### Figshare Token
1. Go to https://figshare.com/account/applications
2. Create a new personal token
3. Copy the token to `FIGSHARE_TOKEN`

#### WordPress App Password
1. Go to your WordPress admin → Users → Profile
2. Scroll to "Application Passwords"
3. Create a new application password
4. Use the generated password (spaces are okay)

## Usage Examples

### Post a New Paper Summary to Website

```python
# AI agent can call:
wp_create_post(
    site="efc",  # or "magnusson"
    title="New EFC Paper: Entropy-Gradient Gravity",
    content="Summary of the paper...",
    categories=["Research", "Papers"],
    status="draft"  # or "publish"
)
```

### Upload to Figshare

```python
figshare_create_article(
    title="EFC Technical Note",
    description="Description...",
    categories=[{"id": 123}],  # Physics category
    keywords=["cosmology", "entropy"],
    defined_type="preprint"
)
```

### Validate Repository

```python
validate_jsonld(path="/jsonld/")
check_links(include_external=True)
```

## Security Notes

- Never commit API tokens to the repository
- Use environment variables or secure credential storage
- The MCP server runs locally with your credentials
- Review all AI-generated content before publishing

## Related Files

- `/auth/manifest.json` - Provenance scope
- `/figshare/sync_log.json` - Sync history
- `/schema/site-graph.json` - Site structure
- `/integrations/wp/schemas/efc-core.json` - WordPress schema
