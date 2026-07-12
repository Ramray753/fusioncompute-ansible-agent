import os
import asyncio
from crewai.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Establish absolute project root directory anchor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# MCP CLIENT INTEGRATION LAYER
# ==============================================================================
SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=[os.path.join(BASE_DIR, "mcp_wrapper", "mcp_server.py")]
)

async def _call_mcp_resource(uri: str) -> str:
    """Asynchronously establishes stdio tunnel to read centralized knowledge resources."""
    async with stdio_client(SERVER_PARAMS) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.read_resource(uri)
            if response and response.contents:
                return response.contents[0].text
            return "Requested resource content layer is empty."

async def _call_mcp_tool(name: str, arguments: dict) -> str:
    """Asynchronously establishes stdio tunnel to execute centralized execution actions."""
    async with stdio_client(SERVER_PARAMS) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.call_tool(name, arguments)
            if response and response.content:
                return response.content[0].text
            return "Target tool action yielded no response payload."

# ==============================================================================
# ROLE-BASED HARD ISOLATED LOOKUP TOOLS (DYNAMIC FACTORY)
# ==============================================================================

def get_role_based_read_tools(script_type: int):
    """
    Factory function to generate role-based read tools dynamically configured 
    for the given script_type to prevent hallucination and resource leaks.
    """
    
    # 1. Define foundational static URIs
    designer_allowed_static_uris = [
        "fc://api/headings",
        "fc://ansible/spec",
        "fc://ansible/example/single"
    ]
    engineer_allowed_static_uris = [
        "fc://api/spec",
        "fc://ansible/spec",
        "fc://ansible/example/single"
    ]
    
    # Append specific batch examples based on dynamic routing
    if script_type == 2:
        designer_allowed_static_uris.append("fc://ansible/example/sequential")
        engineer_allowed_static_uris.append("fc://ansible/example/sequential")
    elif script_type == 3:
        designer_allowed_static_uris.append("fc://ansible/example/parallel")
        engineer_allowed_static_uris.append("fc://ansible/example/parallel")

    # 2. Dynamically construct docstrings so the LLM only "sees" the permitted URIs
    designer_doc = (
        "Read-only context acquisition tool restricted strictly to the [Automation Architect].\n"
        "Input 'uri' must exactly match one of the following predefined FC resources or dynamic content API strings.\n"
    ) + "".join([f"    - \"{uri}\"\n" for uri in designer_allowed_static_uris]) + "    - \"fc://api/content/<keyword>\""
    
    engineer_doc = (
        "Read-only context acquisition tool restricted strictly to the [Code Engineer].\n"
        "Input 'uri' must exactly match one of the following predefined FC resources or dynamic content API strings.\n"
    ) + "".join([f"    - \"{uri}\"\n" for uri in engineer_allowed_static_uris]) + "    - \"fc://api/content/<keyword>\""

    # 3. Create the tools with physical interception logic
    @tool("designer_read_mcp_resource")
    def designer_read_mcp_resource(uri: str) -> str:
        """Dynamic Description applied below."""
        
        # [PHYSICAL INTERCEPTION] Hard block hallucinatory cross-routing access
        if "example/sequential" in uri and script_type != 2:
            return "[FATAL ERROR] Permission denied. Sequential batch example is restricted in current operation mode."
        if "example/parallel" in uri and script_type != 3:
            return "[FATAL ERROR] Permission denied. Parallel batch example is restricted in current operation mode."
            
        if uri not in designer_allowed_static_uris and not uri.startswith("fc://api/content/"):
            return f"[SECURITY ACCESS DENIED] The Automation Architect is unauthorized to pull context from URI: '{uri}'"

        try:
            return asyncio.run(_call_mcp_resource(uri))
        except Exception as error:
            return f"[MCP CLIENT ERROR] Failed to read resource context at '{uri}'. Details: {str(error)}"

    @tool("engineer_read_mcp_resource")
    def engineer_read_mcp_resource(uri: str) -> str:
        """Dynamic Description applied below."""
        
        # [PHYSICAL INTERCEPTION] Hard block hallucinatory cross-routing access
        if "example/sequential" in uri and script_type != 2:
            return "[FATAL ERROR] Permission denied. Sequential batch example is restricted in current operation mode."
        if "example/parallel" in uri and script_type != 3:
            return "[FATAL ERROR] Permission denied. Parallel batch example is restricted in current operation mode."
            
        if uri not in engineer_allowed_static_uris and not uri.startswith("fc://api/content/"):
            return f"[SECURITY ACCESS DENIED] The Code Engineer is unauthorized to pull context from URI: '{uri}'"

        try:
            return asyncio.run(_call_mcp_resource(uri))
        except Exception as error:
            return f"[MCP CLIENT ERROR] Failed to read resource context at '{uri}'. Details: {str(error)}"

    @tool("reviewer_read_mcp_resource")
    def reviewer_read_mcp_resource(uri: str) -> str:
        """
        Read-only context acquisition tool restricted strictly to the [Code Reviewer].
        Input 'uri' must exactly match one of the following predefined FC resources or dynamic content API strings.
        - "fc://ansible/spec",
        - "fc://api/spec"
        - "fc://api/content/<keyword>"
        """
        allowed_static_uris = [
            "fc://ansible/spec",
            "fc://api/spec"
        ]
        if uri not in allowed_static_uris and not uri.startswith("fc://api/content/"):
            return f"[SECURITY ACCESS DENIED] The Code Reviewer is unauthorized to pull context from URI: '{uri}'"

        try:
            return asyncio.run(_call_mcp_resource(uri))
        except Exception as error:
            return f"[MCP CLIENT ERROR] Failed to read resource context at '{uri}'. Details: {str(error)}"

    # Override descriptions natively to ensure the LLM parses the updated route URIs
    designer_read_mcp_resource.description = designer_doc
    engineer_read_mcp_resource.description = engineer_doc

    return designer_read_mcp_resource, engineer_read_mcp_resource, reviewer_read_mcp_resource

# ==============================================================================
# MCP ACTION TOOLS (With Physical File-System Side-Effects)
# ==============================================================================

@tool("initialize_output_dir")
def initialize_output_dir() -> str:
    """Creates the target output directory and copies whitelisted system files."""
    try:
        return asyncio.run(_call_mcp_tool("initialize_output_dir", {}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to initialize directory. Details: {str(error)}"

@tool("write_modular_ansible_files")
def write_modular_ansible_files(file_matrix: dict) -> str:
    """Physical write operation to deploy generated playbook files to the disk workspace."""
    try:
        return asyncio.run(_call_mcp_tool("write_modular_ansible_files", {"file_matrix": file_matrix}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to commit files to disk matrix. Details: {str(error)}"

@tool("read_workspace_playbook_file")
def read_workspace_playbook_file(file_name: str) -> str:
    """Physical read operation allowing pulling generated source code from the workspace."""
    try:
        return asyncio.run(_call_mcp_tool("read_workspace_playbook_file", {"file_name": file_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to read target source file from workspace. Details: {str(error)}"

@tool("validate_yaml_jinja_ast")
def validate_yaml_jinja_ast(file_name: str) -> str:
    """Physical static analysis to validate YAML and Jinja2 AST compliance."""
    try:
        return asyncio.run(_call_mcp_tool("validate_yaml_jinja_ast", {"file_name": file_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to validate AST. Details: {str(error)}"

@tool("run_ansible_syntax_check")
def run_ansible_syntax_check(playbook_name: str) -> str:
    """Native Ansible syntax verification using the local ansible-playbook CLI runtime."""
    try:
        return asyncio.run(_call_mcp_tool("run_ansible_syntax_check", {"playbook_name": playbook_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to run syntax check. Details: {str(error)}"