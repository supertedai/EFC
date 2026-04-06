# EFC Integrations

Integration layer for Energy-Flow Cosmology (EFC), providing machine-readable interfaces for AI agents and content management systems. This directory bridges the EFC research repository with external platforms, enabling automated publishing, resource management, and AI-assisted scientific workflows.

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)), Symbiose Research, Sandnes, Norway
**License:** CC-BY-4.0
**Repository:** <https://github.com/supertedai/EFC>

## Directory Structure

```
integrations/
├── mcp/                 # Model Context Protocol server for AI agents
│   ├── efc_mcp_server.py    # Main MCP server implementation
│   ├── server.json          # Server configuration and tool definitions
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # MCP-specific documentation
│
└── wp/                  # WordPress integration layer
    └── schemas/
        └── efc-core.json    # Schema.org structured data for WordPress sites
```

## MCP Server (`mcp/`)

The MCP (Model Context Protocol) server enables AI agents to interact programmatically with EFC resources across four surfaces:

1. **EFC Repository** -- Read, write, and validate files in the GitHub repository.
2. **energyflow-cosmology.com** -- Publish and manage content on the primary EFC website (WordPress).
3. **magnusson.as** -- Publish and manage content on the hypothesis platform (WordPress).
4. **Figshare** -- Manage and publish research outputs to Figshare for DOI-persistent archival.

### Prerequisites

- Python 3.10 or later
- MCP SDK (`pip install mcp`)

### Installation

```bash
cd integrations/mcp
pip install -r requirements.txt
```

### Configuration

Set environment variables before running the server:

```bash
export EFC_ROOT="/path/to/EFC"           # Root of the EFC repository
export FIGSHARE_TOKEN="your_token"       # Figshare API token (optional)
export WP_USER="username"                # WordPress username (optional)
export WP_APP_PASSWORD="password"        # WordPress application password (optional)
```

### Running the MCP Server

```bash
python efc_mcp_server.py
```

The server exposes tools for AI agents via the MCP protocol, including WordPress post management (`wp_list_posts`, `wp_create_post`), repository operations, and Figshare publication management. The full tool catalog is defined in `server.json`.

### Connecting an AI Agent

Point your MCP-compatible client (e.g., Claude Desktop, Claude Code) to the server using the configuration in `server.json`. The server advertises its capabilities and available tools on connection, allowing agents to discover and invoke operations dynamically.

## WordPress Integration (`wp/`)

The `wp/` directory provides structured data schemas for WordPress sites hosting EFC content. The core schema (`wp/schemas/efc-core.json`) defines a Schema.org `@graph` containing:

- A `ResearchProject` node describing the EFC initiative, its keywords, and principal investigator.
- A `Person` node for the author with linked identities (Figshare, GitHub).

This schema is injected into WordPress pages as JSON-LD, enabling search engines and AI agents to discover EFC as a structured research entity rather than unstructured web content.

## For AI Agents

If you are an AI agent reading this directory:

- **To manage EFC resources**, connect to the MCP server defined in `mcp/server.json`.
- **To understand EFC identity**, parse `wp/schemas/efc-core.json` for Schema.org structured data.
- **To discover EFC content**, see the `jsonld/` directory at the repository root for 59 JSON-LD metadata files covering all published papers and specifications.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `mcp` | >= 0.1.0 | Model Context Protocol SDK |
| `requests` | >= 2.28.0 | HTTP API calls |
| `pyld` | >= 2.0.0 | JSON-LD processing (optional) |
| `aiohttp` | >= 3.8.0 | Async operations (optional) |
| `python-dotenv` | >= 1.0.0 | Environment variable management |

## Related Directories

- `/jsonld/` -- Semantic metadata files consumed by the MCP server
- `/meta/symbiosis/` -- Human-AI collaboration architecture and context
- `/pipelines/` -- Computational pipelines whose outputs can be published via MCP
