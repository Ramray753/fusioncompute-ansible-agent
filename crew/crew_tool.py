import os
import asyncio
import concurrent.futures
from crewai.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# [MODIFIED] Use relative imports for the centralized logger
from .crew_log import logger

# [MODIFIED] Establish absolute project root directory anchor.
# Added an extra os.path.dirname() to step out of the 'crew/' folder and point to the root.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==============================================================================
# ASYNC EXECUTION HELPER (DEFENSIVE PROGRAMMING)
# ==============================================================================
def _run_async_safely(coro):
    """
    Safely executes a coroutine synchronously, avoiding event loop conflicts.
    Ensures the Tool always returns a string payload instead of an awaited Task,
    preventing 'asyncio.run() cannot be called from a running event loop' errors.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
        
    if loop and loop.is_running():
        # Spawn a separate thread to run the async loop cleanly
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        # Standard execution if no loop exists
        return asyncio.run(coro)

# ==============================================================================
# MCP CLIENT INTEGRATION LAYER
# ==============================================================================
SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=[os.path.join(BASE_DIR, "mcp_wrapper", "mcp_server.py")]
)

async def _call_mcp_resource(uri: str) -> str:
    """Asynchronously establishes stdio tunnel to read centralized knowledge resources."""
    # [MODIFIED] Intercept and log the exact URI requested by the Agent before establishing the tunnel
    logger.info(f"[MCP RESOURCE EXECUTION] Triggering read access for URI: '{uri}'")
    
    async with stdio_client(SERVER_PARAMS) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.read_resource(uri)
            if response and response.contents:
                return response.contents[0].text
            return "Requested resource content layer is empty."

async def _call_mcp_tool(name: str, arguments: dict) -> str:
    """Asynchronously establishes stdio tunnel to execute centralized execution actions."""
    # [MODIFIED] Intercept and log the exact tool name and dynamic parameters requested by the Agent
    logger.info(f"[MCP TOOL EXECUTION] Triggering action: '{name}' | Parameters injected: {arguments}")
    
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
        "fc://api/spec", # [ADDED] Allow Architect to understand global URIs and Object IDs
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
    
    reviewer_doc = (
        "Read-only context acquisition tool restricted strictly to the [Code Reviewer].\n"
        "Input 'uri' must exactly match one of the following predefined FC resources or dynamic content API strings.\n"
        "    - \"fc://ansible/spec\"\n"
        "    - \"fc://api/spec\"\n"
        "    - \"fc://api/content/<keyword>\""
    )

    # 3. Define raw tool functions with physical interception logic
    def _designer_read(uri: str) -> str:
        # [PHYSICAL INTERCEPTION] Hard block hallucinatory cross-routing access
        if "example/sequential" in uri and script_type != 2:
            return "[FATAL ERROR] Permission denied. Sequential batch example is restricted in current operation mode."
        if "example/parallel" in uri and script_type != 3:
            return "[FATAL ERROR] Permission denied. Parallel batch example is restricted in current operation mode."
            
        if uri not in designer_allowed_static_uris and not uri.startswith("fc://api/content/"):
            return f"[SECURITY ACCESS DENIED] The Automation Architect is unauthorized to pull context from URI: '{uri}'"

        try:
            return _run_async_safely(_call_mcp_resource(uri))
        except Exception as error:
            return f"[MCP CLIENT ERROR] Failed to read resource context at '{uri}'. Details: {str(error)}"

    def _engineer_read(uri: str) -> str:
        # [PHYSICAL INTERCEPTION] Hard block hallucinatory cross-routing access
        if "example/sequential" in uri and script_type != 2:
            return "[FATAL ERROR] Permission denied. Sequential batch example is restricted in current operation mode."
        if "example/parallel" in uri and script_type != 3:
            return "[FATAL ERROR] Permission denied. Parallel batch example is restricted in current operation mode."
            
        if uri not in engineer_allowed_static_uris and not uri.startswith("fc://api/content/"):
            return f"[SECURITY ACCESS DENIED] The Code Engineer is unauthorized to pull context from URI: '{uri}'"

        try:
            return _run_async_safely(_call_mcp_resource(uri))
        except Exception as error:
            return f"[MCP CLIENT ERROR] Failed to read resource context at '{uri}'. Details: {str(error)}"

    def _reviewer_read(uri: str) -> str:
        allowed_static_uris = [
            "fc://ansible/spec",
            "fc://api/spec"
        ]
        if uri not in allowed_static_uris and not uri.startswith("fc://api/content/"):
            return f"[SECURITY ACCESS DENIED] The Code Reviewer is unauthorized to pull context from URI: '{uri}'"

        try:
            return _run_async_safely(_call_mcp_resource(uri))
        except Exception as error:
            return f"[MCP CLIENT ERROR] Failed to read resource context at '{uri}'. Details: {str(error)}"

    # 4. Instantiate explicitly using the Tool class to guarantee stable schema injection
    _designer_read.__doc__ = designer_doc
    designer_read_tool = tool("designer_read_mcp_resource")(_designer_read)
    
    _engineer_read.__doc__ = engineer_doc
    engineer_read_tool = tool("engineer_read_mcp_resource")(_engineer_read)
    
    _reviewer_read.__doc__ = reviewer_doc
    reviewer_read_tool = tool("reviewer_read_mcp_resource")(_reviewer_read)

    return designer_read_tool, engineer_read_tool, reviewer_read_tool

# ==============================================================================
# MCP ACTION TOOLS (With Physical File-System Side-Effects)
# ==============================================================================

@tool("initialize_output_dir")
def initialize_output_dir() -> str:
    """
    Creates the target output directory and copies whitelisted system files.
    Requires no arguments.
    """
    try:
        return _run_async_safely(_call_mcp_tool("initialize_output_dir", {}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to initialize directory. Details: {str(error)}"

@tool("write_modular_ansible_files")
def write_modular_ansible_files(file_matrix: dict) -> str:
    """
    Physical write operation to deploy generated playbook files to the disk workspace.
    
    Args:
        file_matrix (dict): A dictionary mapping exact file names (e.g., 'main.yml', 'commons.yml')
                            to their raw string content.
    """
    try:
        return _run_async_safely(_call_mcp_tool("write_modular_ansible_files", {"file_matrix": file_matrix}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to commit files to disk matrix. Details: {str(error)}"

@tool("read_workspace_playbook_file")
def read_workspace_playbook_file(file_name: str) -> str:
    """
    Physical read operation allowing pulling generated source code from the workspace.
    
    Args:
        file_name (str): The exact name of the playbook file to read (e.g., 'main.yml').
    """
    # [MODIFIED] Hard block access to the system-protected wait task playbook.
    # This physically prevents the Agent from wasting tokens or hallucinating 
    # reviews on immutable system files.
    if file_name == "wait_fc_system_task.yml":
        return "[SECURITY BLOCK] Access denied. 'wait_fc_system_task.yml' is a pre-validated, immutable system file. You are STRICTLY PROHIBITED from reading, reviewing, or modifying it. Proceed with reviewing other generated files."
        
    try:
        return _run_async_safely(_call_mcp_tool("read_workspace_playbook_file", {"file_name": file_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to read target source file from workspace. Details: {str(error)}"

@tool("validate_yaml_jinja_ast")
def validate_yaml_jinja_ast(file_name: str) -> str:
    """
    Physical static analysis to validate YAML and Jinja2 AST compliance locally.
    
    Args:
        file_name (str): The target file to validate (e.g., 'main.yml').
    """
    try:
        return _run_async_safely(_call_mcp_tool("validate_yaml_jinja_ast", {"file_name": file_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to validate AST. Details: {str(error)}"

@tool("run_ansible_syntax_check")
def run_ansible_syntax_check(playbook_name: str) -> str:
    """
    Native Ansible syntax verification using the local ansible-playbook CLI runtime.
    
    Args:
        playbook_name (str): The entry point file name to run the syntax check against (e.g., 'main.yml').
    """
    try:
        return _run_async_safely(_call_mcp_tool("run_ansible_syntax_check", {"playbook_name": playbook_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to run syntax check. Details: {str(error)}"