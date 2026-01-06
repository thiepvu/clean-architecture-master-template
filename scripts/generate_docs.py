#!/usr/bin/env python3
"""
API Documentation Generator
===========================

Generate API documentation in Markdown format from OpenAPI schema.

Features
--------
- Fetches OpenAPI JSON schema from running server
- Converts to readable Markdown documentation
- Generates table of contents, endpoints by tag, and schemas
- Saves both Markdown and raw JSON for reference

Usage
-----
```bash
# Start server first
python src/main.py --env development

# Generate docs (default: from localhost:8000)
python scripts/generate_docs.py

# Custom URL and output
python scripts/generate_docs.py --url http://localhost:8000/api/openapi.json --output docs/API.md
```

Requirements
------------
- Server must be running to fetch OpenAPI schema
- requests library installed

Exit Codes
----------
- 0: Success
- 1: Error (server not running, fetch failed, etc.)
"""
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

import requests

from shared.bootstrap import create_config_service, create_logger

# Initialize config service and logger (bootstrap level - uses helpers)
config_service = create_config_service()
logger = create_logger(config_service=config_service)


class OpenAPIToMarkdown:
    """Convert OpenAPI JSON schema to Markdown documentation"""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.info = schema.get("info", {})
        self.servers = schema.get("servers", [])
        self.paths = schema.get("paths", {})
        self.components = schema.get("components", {})
        self.tags = schema.get("tags", [])
        self.security = schema.get("security", [])

    def generate(self) -> str:
        """Generate complete Markdown documentation"""
        sections = [
            self._generate_header(),
            self._generate_table_of_contents(),
            self._generate_info(),
            self._generate_servers(),
            self._generate_authentication(),
            self._generate_tags_section(),
            self._generate_endpoints(),
            self._generate_schemas(),
        ]
        
        return "\n\n".join(filter(None, sections))

    def _generate_header(self) -> str:
        """Generate document header"""
        title = self.info.get("title", "API Documentation")
        version = self.info.get("version", "1.0.0")
        
        return f"""# {title}

**Version:** {version}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
"""

    def _generate_table_of_contents(self) -> str:
        """Generate table of contents"""
        toc = ["## Table of Contents\n"]
        
        toc.append("- [Overview](#overview)")
        toc.append("- [Servers](#servers)")
        toc.append("- [Authentication](#authentication)")
        
        if self.tags:
            toc.append("- [Endpoints by Tag](#endpoints-by-tag)")
            for tag in self.tags:
                tag_name = tag.get("name", "")
                anchor = tag_name.lower().replace(" ", "-")
                toc.append(f"  - [{tag_name}](#{anchor})")
        
        toc.append("- [All Endpoints](#all-endpoints)")
        toc.append("- [Schemas](#schemas)")
        
        return "\n".join(toc)

    def _generate_info(self) -> str:
        """Generate overview section"""
        description = self.info.get("description", "No description provided.")
        
        return f"""## Overview

{description}
"""

    def _generate_servers(self) -> str:
        """Generate servers section"""
        if not self.servers:
            return ""
        
        lines = ["## Servers\n"]
        
        for server in self.servers:
            url = server.get("url", "")
            description = server.get("description", "")
            lines.append(f"- **{url}**")
            if description:
                lines.append(f"  - {description}")
        
        return "\n".join(lines)

    def _generate_authentication(self) -> str:
        """Generate authentication section"""
        security_schemes = self.components.get("securitySchemes", {})
        
        if not security_schemes:
            return ""
        
        lines = ["## Authentication\n"]
        
        for scheme_name, scheme in security_schemes.items():
            scheme_type = scheme.get("type", "")
            lines.append(f"### {scheme_name}\n")
            lines.append(f"**Type:** `{scheme_type}`")
            
            if scheme_type == "http":
                lines.append(f"**Scheme:** `{scheme.get('scheme', '')}`")
                bearer_format = scheme.get("bearerFormat")
                if bearer_format:
                    lines.append(f"**Bearer Format:** `{bearer_format}`")
            
            description = scheme.get("description")
            if description:
                lines.append(f"\n{description}")
            
            lines.append("")
        
        return "\n".join(lines)

    def _generate_tags_section(self) -> str:
        """Generate tags overview section"""
        if not self.tags:
            return ""
        
        lines = ["## Endpoints by Tag\n"]
        
        for tag in self.tags:
            name = tag.get("name", "")
            description = tag.get("description", "")
            
            lines.append(f"### {name}\n")
            if description:
                lines.append(f"{description}\n")
        
        return "\n".join(lines)

    def _generate_endpoints(self) -> str:
        """Generate all endpoints documentation"""
        lines = ["## All Endpoints\n"]
        
        # Group endpoints by tag
        endpoints_by_tag = self._group_endpoints_by_tag()
        
        for tag_name, endpoints in endpoints_by_tag.items():
            anchor = tag_name.lower().replace(" ", "-")
            lines.append(f"### {tag_name} {{#{anchor}}}\n")
            
            for endpoint in endpoints:
                lines.append(self._generate_endpoint(endpoint))
                lines.append("---\n")
        
        return "\n".join(lines)

    def _group_endpoints_by_tag(self) -> Dict[str, List[Dict]]:
        """Group endpoints by their tags"""
        grouped = {}
        
        for path, methods in self.paths.items():
            for method, details in methods.items():
                if method.startswith("x-"):  # Skip extension fields
                    continue
                
                tags = details.get("tags", ["Untagged"])
                
                for tag in tags:
                    if tag not in grouped:
                        grouped[tag] = []
                    
                    grouped[tag].append({
                        "path": path,
                        "method": method.upper(),
                        "details": details,
                    })
        
        return grouped

    def _generate_endpoint(self, endpoint: Dict) -> str:
        """Generate documentation for a single endpoint"""
        path = endpoint["path"]
        method = endpoint["method"]
        details = endpoint["details"]
        
        lines = []
        
        # Endpoint title
        summary = details.get("summary", path)
        lines.append(f"#### `{method}` {path}\n")
        lines.append(f"**Summary:** {summary}\n")
        
        # Description
        description = details.get("description")
        if description:
            lines.append(f"{description}\n")
        
        # Parameters
        parameters = details.get("parameters", [])
        if parameters:
            lines.append("**Parameters:**\n")
            lines.append("| Name | In | Type | Required | Description |")
            lines.append("|------|-------|------|----------|-------------|")
            
            for param in parameters:
                name = param.get("name", "")
                in_location = param.get("in", "")
                required = "Yes" if param.get("required", False) else "No"
                param_schema = param.get("schema", {})
                param_type = param_schema.get("type", "string")
                param_description = param.get("description", "")
                
                lines.append(f"| `{name}` | {in_location} | {param_type} | {required} | {param_description} |")
            
            lines.append("")
        
        # Request Body
        request_body = details.get("requestBody")
        if request_body:
            lines.append("**Request Body:**\n")
            content = request_body.get("content", {})
            
            for content_type, content_details in content.items():
                lines.append(f"- **Content-Type:** `{content_type}`")
                schema = content_details.get("schema", {})
                
                if "$ref" in schema:
                    ref_name = schema["$ref"].split("/")[-1]
                    lines.append(f"- **Schema:** [{ref_name}](#schema-{ref_name.lower()})")
                else:
                    lines.append(f"- **Schema:**")
                    lines.append(f"```json")
                    lines.append(json.dumps(schema, indent=2))
                    lines.append(f"```")
            
            lines.append("")
        
        # Responses
        responses = details.get("responses", {})
        if responses:
            lines.append("**Responses:**\n")
            
            for status_code, response in responses.items():
                description = response.get("description", "")
                lines.append(f"- **{status_code}**: {description}")
                
                content = response.get("content", {})
                for content_type, content_details in content.items():
                    schema = content_details.get("schema", {})
                    if "$ref" in schema:
                        ref_name = schema["$ref"].split("/")[-1]
                        lines.append(f"  - **Content-Type:** `{content_type}`")
                        lines.append(f"  - **Schema:** [{ref_name}](#schema-{ref_name.lower()})")
            
            lines.append("")
        
        # Security
        security = details.get("security")
        if security:
            lines.append("**Security:**")
            for sec in security:
                for scheme_name, scopes in sec.items():
                    scopes_str = ", ".join(scopes) if scopes else "None"
                    lines.append(f"- {scheme_name} (Scopes: {scopes_str})")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_schemas(self) -> str:
        """Generate schemas documentation"""
        schemas = self.components.get("schemas", {})
        
        if not schemas:
            return ""
        
        lines = ["## Schemas\n"]
        
        for schema_name, schema_details in schemas.items():
            anchor = schema_name.lower()
            lines.append(f"### {schema_name} {{#schema-{anchor}}}\n")
            
            schema_type = schema_details.get("type", "object")
            lines.append(f"**Type:** `{schema_type}`\n")
            
            description = schema_details.get("description")
            if description:
                lines.append(f"{description}\n")
            
            properties = schema_details.get("properties", {})
            if properties:
                lines.append("**Properties:**\n")
                lines.append("| Property | Type | Required | Description |")
                lines.append("|----------|------|----------|-------------|")
                
                required_fields = schema_details.get("required", [])
                
                for prop_name, prop_details in properties.items():
                    prop_type = prop_details.get("type", "string")
                    is_required = "Yes" if prop_name in required_fields else "No"
                    prop_description = prop_details.get("description", "")
                    
                    # Handle refs
                    if "$ref" in prop_details:
                        ref_name = prop_details["$ref"].split("/")[-1]
                        prop_type = f"[{ref_name}](#schema-{ref_name.lower()})"
                    
                    lines.append(f"| `{prop_name}` | {prop_type} | {is_required} | {prop_description} |")
                
                lines.append("")
            
            # Example
            example = schema_details.get("example")
            if example:
                lines.append("**Example:**\n")
                lines.append("```json")
                lines.append(json.dumps(example, indent=2))
                lines.append("```\n")
        
        return "\n".join(lines)


def fetch_openapi_schema(url: str) -> Dict[str, Any]:
    """Fetch OpenAPI schema from URL"""
    try:
        logger.info(f"Fetching OpenAPI schema from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch OpenAPI schema: {e}")
        raise


def save_markdown(content: str, output_path: Path) -> None:
    """Save Markdown content to file"""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"✅ Documentation saved to: {output_path}")
    except IOError as e:
        logger.error(f"Failed to save documentation: {e}")
        raise


def generate_markdown_docs(
    openapi_url: str = None,
    output_file: str = "docs/API_DOCS.md"
) -> None:
    """
    Generate Markdown documentation from OpenAPI schema
    
    Args:
        openapi_url: URL to fetch OpenAPI schema (default: from settings)
        output_file: Output file path for Markdown docs
    """
    # Use provided URL or construct from config service
    if openapi_url is None:
        openapi_url = f"{config_service.base.SERVER_URL}/api/openapi.json"
    
    logger.info("🚀 Starting API documentation generation...")
    
    # Fetch schema
    schema = fetch_openapi_schema(openapi_url)
    logger.info(f"✓ Schema fetched: {schema.get('info', {}).get('title', 'Unknown')}")
    
    # Generate Markdown
    converter = OpenAPIToMarkdown(schema)
    markdown_content = converter.generate()
    logger.info("✓ Markdown content generated")
    
    # Save to file
    output_path = Path(output_file)
    save_markdown(markdown_content, output_path)
    
    # Also save raw JSON for reference
    json_output = output_path.parent / "openapi_schema.json"
    json_output.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    logger.info(f"✓ Raw OpenAPI schema saved to: {json_output}")
    
    logger.info("✅ Documentation generation completed!")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate API documentation from OpenAPI schema"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="OpenAPI schema URL (default: from settings)",
        default=None,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: docs/API_DOCS.md)",
        default="docs/API_DOCS.md",
    )

    args = parser.parse_args()

    try:
        generate_markdown_docs(
            openapi_url=args.url,
            output_file=args.output,
        )
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Documentation generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()