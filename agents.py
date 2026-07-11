import os
import sys
import yaml
import asyncio
from dotenv import load_dotenv
from crewai import Agent, LLM
from crewai.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_wrapper.mcp_prompts import _dict_to_xml

# Establish absolute project root directory anchor (current folder for root agents.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure the project root is in sys.path to resolve internal modules securely
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


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

def build_xml_backstory(agent_config: dict) -> str:
    """
    Extracts granular configuration keys (excluding role and goal) and 
    renders them dynamically into an XML-formatted backstory string.
    """
    dynamic_keys = {k: v for k, v in agent_config.items() if k not in ["role", "goal"]}
    return _dict_to_xml(dynamic_keys, indent_level=1)

# Instantiate the decoupled model processing components securely using native LLM types
analyst_llm = bootstrap_runtime_llm("ANALYST_MODEL", "ANALYST_BASE_URL")
coding_llm = bootstrap_runtime_llm("CODING_MODEL", "CODING_BASE_URL")

# Load fully decoupled prompt configurations from local storage matrix
agent_prompts = _load_agent_prompt_config()

# ==============================================================================
# MCP CLIENT INTEGRATION LAYER (Replaces direct tools_ansible hardcoding)
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
# ROLE-BASED HARD ISOLATED LOOKUP TOOLS
# ==============================================================================

@tool("designer_read_mcp_resource")
def designer_read_mcp_resource(uri: str) -> str:
    """
    Read-only context acquisition tool restricted strictly to the [Automation Architect].
    Input 'uri' must exactly match one of the following strings:
    - 'fc://api/headings' : To discover system capabilities and plan workflows.
    - 'fc://ansible/spec' : To examine specific module syntax constraints.
    - 'fc://ansible/example/single' : To analyze single operation layouts and logs.
    - 'fc://ansible/example/sequential' : To analyze sequential batch looping patterns and logs.
    - 'fc://ansible/example/parallel' : To analyze concurrent parallel processing patterns and logs.
    - 'fc://api/content/{keyword}' : Replace {keyword} with the exact literal Chinese section name (e.g., 'fc://api/content/查询指定主机') to fetch precise parameter schemas.
    """
    allowed_static_uris = [
        "fc://api/headings",
        "fc://ansible/spec",
        "fc://ansible/example/single",
        "fc://ansible/example/sequential",
        "fc://ansible/example/parallel"
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
    Input 'uri' must exactly match one of the following strings:
    - 'fc://ansible/spec' : To examine specific module syntax constraints.
    - 'fc://api/spec' : To parse global API baseline standards and URL formats.
    - 'fc://ansible/example/single' : To retrieve single operation layouts and execution logs.
    - 'fc://ansible/example/sequential' : To map ordered batch file matrices correctly.
    - 'fc://ansible/example/parallel' : To map high-concurrency loops accurately.
    - 'fc://api/content/{keyword}' : Replace {keyword} with the exact literal Chinese section name (e.g., 'fc://api/content/查询指定主机') to retrieve full parameter payload schemas.
    """
    allowed_static_uris = [
        "fc://ansible/spec",
        "fc://api/spec",
        "fc://ansible/example/single",
        "fc://ansible/example/sequential",
        "fc://ansible/example/parallel"
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
    Input 'uri' must exactly match one of the following strings:
    - 'fc://ansible/spec' : To verify if generated blocks match framework standards.
    - 'fc://api/spec' : To audit relative paths cleanliness and URL constraints.
    - 'fc://api/content/{keyword}' : Replace {keyword} with the exact literal Chinese section name to audit parameter completeness.
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

# ==============================================================================
# MCP ACTION TOOLS (With Physical File-System Side-Effects)
# ==============================================================================

@tool("initialize_output_dir")
def initialize_output_dir() -> str:
    """
    Creates the target output directory and copies whitelisted system files (e.g., wait_fc_system_task.yml).
    Execution Constraint: You MUST call this tool exactly once BEFORE making any calls to 'write_modular_ansible_files'.
    No arguments are required.
    """
    try:
        return asyncio.run(_call_mcp_tool("initialize_output_dir", {}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to initialize directory. Details: {str(error)}"

@tool("write_modular_ansible_files")
def write_modular_ansible_files(file_matrix: dict) -> str:
    """
    Physical write operation to deploy generated playbook files to the disk workspace.
    Argument 'file_matrix' MUST be a flat dictionary where the key is the exact filename 
    including extension (e.g., 'main.yml', 'commons.yml', 'process.py') and the value is the raw string code content.
    Example Input Structure: {"main.yml": "---\n- hosts: localhost...", "commons.yml": "var: 123"}
    Do NOT include protected system files like 'wait_fc_system_task.yml' in the matrix.
    """
    try:
        return asyncio.run(_call_mcp_tool("write_modular_ansible_files", {"file_matrix": file_matrix}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to commit files to disk matrix. Details: {str(error)}"

@tool("read_workspace_playbook_file")
def read_workspace_playbook_file(file_name: str) -> str:
    """
    Physical read operation allowing pulling generated source code from the workspace for compliance auditing.
    Argument 'file_name' MUST be the exact filename without any directory paths (e.g., 'main.yml' or 'commons.yml').
    """
    try:
        return asyncio.run(_call_mcp_tool("read_workspace_playbook_file", {"file_name": file_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to read target source file from workspace. Details: {str(error)}"

@tool("validate_yaml_jinja_ast")
def validate_yaml_jinja_ast(file_name: str) -> str:
    """
    Physical static analysis to validate YAML and Jinja2 AST compliance.
    Argument 'file_name' MUST be the exact target filename (e.g., 'main.yml').
    Execution Constraint: You are STRICTLY PROHIBITED from running this tool on 'wait_fc_system_task.yml'.
    """
    try:
        return asyncio.run(_call_mcp_tool("validate_yaml_jinja_ast", {"file_name": file_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to validate AST. Details: {str(error)}"

@tool("run_ansible_syntax_check")
def run_ansible_syntax_check(playbook_name: str) -> str:
    """
    Native Ansible syntax verification using the local ansible-playbook CLI runtime.
    Argument 'playbook_name' MUST be the primary execution entry point file, which is always 'main.yml'.
    """
    try:
        return asyncio.run(_call_mcp_tool("run_ansible_syntax_check", {"playbook_name": playbook_name}))
    except Exception as error:
        return f"[MCP CLIENT ERROR] Failed to run syntax check. Details: {str(error)}"

# ==============================================================================
# AGENT 1: BLUEPRINT ARCHITECTURE DESIGNER ([Automation Architect])
# ==============================================================================
p_designer = agent_prompts["ansible_blueprint_designer"]
ansible_blueprint_designer = Agent(
    role=p_designer["role"],
    goal=p_designer["goal"],
    backstory=build_xml_backstory(p_designer),
    tools=[designer_read_mcp_resource],
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
    backstory=build_xml_backstory(p_engineer),
    tools=[
        engineer_read_mcp_resource, 
        initialize_output_dir,
        write_modular_ansible_files
    ], 
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
    backstory=build_xml_backstory(p_reviewer),
    tools=[
        reviewer_read_mcp_resource, 
        write_modular_ansible_files, 
        read_workspace_playbook_file,
        validate_yaml_jinja_ast, 
        run_ansible_syntax_check
    ], 
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

    # Test 2: Verify Code Compilation Engineer tool isolation boundary (Updated to 3 for read + write + init MCP bounds)
    assert len(ansible_code_engineer.tools) == 3, f"Error: Code Engineer must possess exactly 3 integration tools. Found: {len(ansible_code_engineer.tools)}"
    print("  Pass: Code Engineer Agent tool volume validated.")

    # Test 3: Verify QA Reviewer Engineer tool isolation boundary (Updated to 5 for physical validations)
    assert len(ansible_code_reviewer.tools) == 5, f"Error: Reviewer must possess exactly 5 validation tools. Found: {len(ansible_code_reviewer.tools)}"
    print("  Pass: Reviewer Agent tool volume and filesystem visibility validated.")
    
    print("\n" + "="*21 + " PIPELINE FACTORY INFRASTRUCTURE GREEN " + "="*21 + "\n")