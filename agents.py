import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, LLM

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
    from the external config matrix 'agents.yaml'.
    """
    config_file = "agents.yaml"
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

# Import the streamlined toolset
from tools_ansible import AnsibleAutomationTools

# ==============================================================================
# AGENT 1: BLUEPRINT ARCHITECTURE DESIGNER ([Automation Architect])
# ==============================================================================
p_designer = agent_prompts["ansible_blueprint_designer"]
ansible_blueprint_designer = Agent(
    role=p_designer["role"],
    goal=p_designer["goal"],
    backstory=p_designer["backstory"],
    tools=[
        AnsibleAutomationTools.fetch_all_api_headings,
        AnsibleAutomationTools.query_specific_api_content,
        AnsibleAutomationTools.read_ansible_module_specification,
        AnsibleAutomationTools.read_ansible_exmaple_code_single,
        AnsibleAutomationTools.read_ansible_exmaple_code_batch_sequential,
        AnsibleAutomationTools.read_ansible_exmaple_code_batch_parallel
    ],
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
    tools=[
        AnsibleAutomationTools.read_ansible_module_specification,
        AnsibleAutomationTools.read_api_specification,
        AnsibleAutomationTools.read_ansible_exmaple_code_single,
        AnsibleAutomationTools.read_ansible_exmaple_code_batch_sequential,
        AnsibleAutomationTools.read_ansible_exmaple_code_batch_parallel,
        AnsibleAutomationTools.query_specific_api_content,
        AnsibleAutomationTools.write_modular_ansible_files
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
    backstory=p_reviewer["backstory"],
    tools=[
        AnsibleAutomationTools.read_all_compiled_ansible_files,
        AnsibleAutomationTools.read_ansible_module_specification,
        AnsibleAutomationTools.read_api_specification,
        AnsibleAutomationTools.read_ansible_exmaple_code_single,
        AnsibleAutomationTools.read_ansible_exmaple_code_batch_sequential,
        AnsibleAutomationTools.read_ansible_exmaple_code_batch_parallel,
        AnsibleAutomationTools.query_specific_api_content,
        AnsibleAutomationTools.write_modular_ansible_files
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

    # Test 1: Verify Architect Agent tool isolation boundary (Updated to 6 for specific blueprint routing)
    assert len(ansible_blueprint_designer.tools) == 6, f"Error: Architect must possess exactly 6 lookup tools. Found: {len(ansible_blueprint_designer.tools)}"
    print("  Pass: Architect Agent tool volume validated.")

    # Test 2: Verify Code Compilation Engineer tool isolation boundary (Updated to 7 for split blueprints)
    assert len(ansible_code_engineer.tools) == 7, f"Error: Code Engineer must possess exactly 7 integration tools. Found: {len(ansible_code_engineer.tools)}"
    print("  Pass: Code Engineer Agent tool volume validated.")

    # Test 3: Verify QA Reviewer Engineer tool isolation boundary (Updated to 8 for comprehensive audit + split blueprints)
    assert len(ansible_code_reviewer.tools) == 8, f"Error: Reviewer must possess exactly 8 validation tools. Found: {len(ansible_code_reviewer.tools)}"
    print("  Pass: Reviewer Agent tool volume and filesystem visibility validated.")

    print("\n" + "="*21 + " PIPELINE FACTORY INFRASTRUCTURE GREEN " + "="*21 + "\n")