import os
import yaml
import asyncio
from dotenv import load_dotenv
from crewai import Agent, LLM
from crewai.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Establish absolute project root directory anchor (current folder for root agents.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# ENVIRONMENT BOOTSTRAPPING & MODEL ROUTING
# ==============================================================================
load_dotenv()

def bootstrap_runtime_llm(model_env_key: str, url_env_key: str) -> LLM:
    """
    Parses configuration strings from the environment matrix and constructs
    a native crewai.LLM instance. Strips off any 'openai/' model prefix to
    intentionally disable API-level native function calling, forcing the engine
    to reliably fall back to the plain-text ReAct parsing state machine.
    """
    raw_model = os.getenv(model_env_key)
    target_url = os.getenv(url_env_key)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not raw_model:
        raise ValueError(f"[FATAL ERROR] Requisite environmental variable '{model_env_key}' is undefined.")
    if not target_url:
        raise ValueError(f"[FATAL ERROR] Requisite environmental variable '{url_env_key}' is undefined.")
    if not api_key:
        raise ValueError("[SECURITY ALERT] Online provider requires 'OPENAI_API_KEY' to be populated.")
    
    cleaned_model = raw_model.split("/")[-1] if "/" in raw_model else raw_model
    
    return LLM(
        model=cleaned_model, 
        base_url=target_url, 
        api_key=api_key,
        temperature=0.1
    )

def _load_agent_prompt_config() -> dict:
    """
    Helper function to load multi-line structural agent personas and rule enforcement strings
    from the external config matrix 'agents.yaml' inside the centralized 'conf/' directory.
    """
    config_file = os.path.join(BASE_DIR, "conf", "agents.yaml")
    if not os.path.exists(config_file):
        config_file = os.path.join(BASE_DIR, "conf", "agents.yml")
        
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"[FATAL ERROR] Requisite prompt asset file '{config_file}' is missing from workspace.")
    
    with open(config_file, "r", encoding="utf-8") as file_handle:
        try:
            return yaml.safe_load(file_handle)
        except Exception as error:
            raise ValueError(f"[PARSING ERROR] Failed to load structural yaml context from {config_file}. Details: {str(error)}")

# Instantiate the decoupled model processing components securely using native LLM types
analyst_llm = bootstrap_runtime_llm("ANALYST_MODEL", "ANALYST_BASE_URL")
coding_llm = bootstrap_runtime_llm("CODING_MODEL", "CODING_BASE_URL")

# Load fully decoupled prompt configurations from local storage matrix
agent_prompts = _load_agent_prompt_config()

# ==============================================================================
# MCP CLIENT INTEGRATION LAYER (Replaces direct tools_ansible hardcoding)
# ==============================================================================
# 🎯 PATH TUNNEL ANCHOR: Route the Stdio client parameter pipeline securely into the new 'mcp/' folder
SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=[os.path.join(BASE_DIR, "mcp", "mcp_server.py")]
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
# ROLE-BASED HARD ISOLATED LOOKUP TOOLS
# ==============================================================================

@tool("designer_read_mcp_resource")
def designer_read_mcp_resource(uri: str) -> str:
    """
    Read-only context acquisition tool restricted strictly to the [Automation Architect].
    Supported URIs for the Designer:
    - fc://api/headings (To discover system capabilities and plan workflows)
    - fc://ansible/spec (To examine specific module syntax constraints)
    - fc://ansible/exmaple/single (To analyze standard single operation playbook layouts)
    - fc://ansible/exmaple/sequential (To analyze sequential file-looping patterns)
    - fc://ansible/exmaple/parallel (To analyze concurrent parallel processing patterns)
    - fc://api/content/{keyword} (Replace {keyword} with exact Chinese section name to find parameters metadata)
    """
    # Hard Whitelist Verification for the Blueprint Designer Role
    allowed_static_uris = [
        "fc://api/headings",
        "fc://ansible/spec",
        "fc://ansible/exmaple/single",
        "fc://ansible/exmaple/sequential",
        "fc://ansible/exmaple/parallel"
    ]
    if uri not in allowed_static_uris and not uri.startswith("fc://api/content/"):
        return f"[SECURITY ACCESS DENIED] The Automation Architect is unauthorized to pull context from URI: '{uri}'"

    try:
        return asyncio.run(_call_mcp_resource(uri))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to read resource context at '{uri}'. Details: {str(error)}"

@tool("engineer_read_mcp_resource")
def engineer_read_mcp_resource(uri: str) -> str:
    """
    Read-only context acquisition tool restricted strictly to the [Code Engineer].
    Supported URIs for the Code Engineer:
    - fc://ansible/spec (To examine specific module syntax constraints)
    - fc://api/spec (To parse global API baseline standards and URL formats)
    - fc://ansible/exmaple/single (To align structure with standard layouts and wrappers)
    - fc://ansible/exmaple/sequential (To map ordered batch file matrices correctly)
    - fc://ansible/exmaple/parallel (To map high-concurrency loops accurately)
    - fc://api/content/{keyword} (Replace {keyword} with exact Chinese section name to retrieve full parameters payload schemas)
    """
    # Hard Whitelist Verification for the Code Engineer Role
    allowed_static_uris = [
        "fc://ansible/spec",
        "fc://api/spec",
        "fc://ansible/exmaple/single",
        "fc://ansible/exmaple/sequential",
        "fc://ansible/exmaple/parallel"
    ]
    if uri not in allowed_static_uris and not uri.startswith("fc://api/content/"):
        return f"[SECURITY ACCESS DENIED] The Code Engineer is unauthorized to pull context from URI: '{uri}'"

    try:
        return asyncio.run(_call_mcp_resource(uri))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to read resource context at '{uri}'. Details: {str(error)}"

@tool("reviewer_read_mcp_resource")
def reviewer_read_mcp_resource(uri: str) -> str:
    """
    Read-only context acquisition tool restricted strictly to the [Code Reviewer].
    Supported URIs for the Code Reviewer:
    - fc://ansible/spec (To verify if generated blocks match framework standards)
    - fc://api/spec (To audit relative paths cleanliness and URL constraints)
    - fc://api/content/{keyword} (Replace {keyword} with exact Chinese section name to audit parameter completeness)
    """
    # Hard Whitelist Verification for the Quality Reviewer Role (Strictly blocked from code template blueprints)
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

# ==============================================================================
# MCP ACTION TOOLS (With Physical File-System Side-Effects)
# ==============================================================================

@tool("write_modular_ansible_files")
def write_modular_ansible_files(file_matrix: dict) -> str:
    """
    Physical write operation deploying a compiled dictionary of Ansible files to disk workspace.
    Accepts a file_matrix mapping relative filenames (e.g., 'main.yml') to code payloads.
    """
    try:
        return asyncio.run(_call_mcp_tool("write_modular_ansible_files", {"file_matrix": file_matrix}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to commit files to disk matrix. Details: {str(error)}"

@tool("read_workspace_playbook_file")
def read_workspace_playbook_file(file_name: str) -> str:
    """
    Physical read operation allowing pulling generated source code from the workspace directory for compliance auditing.
    """
    try:
        return asyncio.run(_call_mcp_tool("read_workspace_playbook_file", {"file_name": file_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to read target source file from workspace. Details: {str(error)}"

# ==============================================================================
# AGENT 1: BLUEPRINT ARCHITECTURE DESIGNER ([Automation Architect])
# ==============================================================================
p_designer = agent_prompts["ansible_blueprint_designer"]
ansible_blueprint_designer = Agent(
    role=p_designer["role"],
    goal=p_designer["goal"],
    backstory=p_designer["backstory"],
    tools=[designer_read_mcp_resource], # Programmatically bounded onto the Designer resource whitelist
    verbose=True,
    allow_delegation=False,
    llm=analyst_llm
)

# ==============================================================================
# AGENT 2: AUTOMATION CODE COMPILATION ENGINEER ([Code Engineer])
# ==============================================================================
p_engineer = agent_prompts["ansible_code_engineer"]
ansible_code_engineer = Agent(
    role=p_engineer["role"],
    goal=p_engineer["goal"],
    backstory=p_engineer["backstory"],
    tools=[engineer_read_mcp_resource, write_modular_ansible_files], # Programmatically bounded onto the Engineer whitelist
    verbose=True,
    allow_delegation=False,
    llm=coding_llm
)

# ==============================================================================
# AGENT 3: AUTOMATION CODE REVIEW & QUALITY ASSURANCE ENGINEER ([Code Reviewer])
# ==============================================================================
p_reviewer = agent_prompts["ansible_code_reviewer"]
ansible_code_reviewer = Agent(
    role=p_reviewer["role"],
    goal=p_reviewer["goal"],
    backstory=p_reviewer["backstory"],
    tools=[reviewer_read_mcp_resource, write_modular_ansible_files, read_workspace_playbook_file], # Bounded onto Reviewer whitelist
    verbose=True,
    allow_delegation=False,
    llm=coding_llm
)

# ==============================================================================
# AUDIT & TOOL QUANTITY UNIT TEST
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*20 + " AUDITING MULTI-AGENT PIPELINE MATRICES " + "="*20)

    # Test 1: Verify Architect Agent tool isolation boundary (Updated to 1 for universal MCP resource router)
    assert len(ansible_blueprint_designer.tools) == 1, f"Error: Architect must possess exactly 1 lookup tool. Found: {len(ansible_blueprint_designer.tools)}"
    print("  Pass: Architect Agent tool volume validated.")

    # Test 2: Verify Code Compilation Engineer tool isolation boundary (Updated to 2 for read + write MCP bounds)
    assert len(ansible_code_engineer.tools) == 2, f"Error: Code Engineer must possess exactly 2 integration tools. Found: {len(ansible_code_engineer.tools)}"
    print("  Pass: Code Engineer Agent tool volume validated.")

    # Test 3: Verify QA Reviewer Engineer tool isolation boundary (Updated to 3 for read + write + review visibility)
    assert len(ansible_code_reviewer.tools) == 3, f"Error: Reviewer must possess exactly 3 validation tools. Found: {len(ansible_code_reviewer.tools)}"
    print("  Pass: Reviewer Agent tool volume and filesystem visibility validated.")

    print("\n" + "="*21 + " PIPELINE FACTORY INFRASTRUCTURE GREEN " + "="*21 + "\n")