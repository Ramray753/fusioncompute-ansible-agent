import os
from dotenv import load_dotenv
from crewai import Agent, LLM

# ==============================================================================
# ENVIRONMENT BOOTSTRAPPING & DYNAMIC MODEL ROUTING
# ==============================================================================
# Synchronize system memory matrix with local configuration keys
load_dotenv()

def bootstrap_runtime_llm(model_env_key: str, url_env_key: str) -> LLM:
    """
    Parses configuration strings from the environment matrix and constructs
    an agnostic, unified LLM object supporting both local Ollama and Cloud Gemini.
    """
    target_model = os.getenv(model_env_key)
    if not target_model:
        raise ValueError(f"[FATAL ERROR] Requisite environmental variable '{model_env_key}' is undefined.")
    
    # Track 1: Cloud Gateway Deployment Routing
    if target_model.startswith("gemini"):
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError(f"[SECURITY ALERT] Cloud provider '{target_model}' requires 'GEMINI_API_KEY' to be populated.")
        return LLM(model=target_model, temperature=0.2)
    
    # Track 2: Local Datacenter Sandboxed Container Routing (Ollama)
    else:
        target_url = os.getenv(url_env_key, "http://127.0.0.1:11434")
        return LLM(model=target_model, base_url=target_url)

# Instantiate the two completely decoupled LLM execution instances
analyst_llm = bootstrap_runtime_llm("ANALYST_MODEL", "ANALYST_BASE_URL")
coding_llm = bootstrap_runtime_llm("CODING_MODEL", "CODING_BASE_URL")

# Import the refactored toolkits with Scheme-A multi-file capabilities
from tools_python import PythonRestTools
from tools_ansible import AnsibleAutomationTools

# ==============================================================================
# ROLE 1: VIRTUALIZATION REQUIREMENTS ANALYST
# ==============================================================================
virtualization_analyst = Agent(
    role="Huawei FusionCompute Cloud Architect & Requirements Analyst",
    goal="Deconstruct ambiguous infrastructure requests and determine the absolute optimal technical automation route.",
    backstory=(
        "You are a master virtualization infrastructure architect at Huawei. "
        "Your sole task is to analyze user requests and explicitly choose the execution path: output 'TRACK: PYTHON_REST' "
        "or 'TRACK: ANSIBLE_PLAYBOOK'. You break down high-level requirements into logical, sequential steps but never "
        "write or generate file outputs directly. You possess a zero-tool read-only profile to maintain separation of concerns."
    ),
    verbose=True,
    allow_delegation=False,
    llm=analyst_llm
)

# ==============================================================================
# ROLE 2: PURE PYTHON REST AUTOMATION ENGINEER (SCHEME A MASTER CODER)
# ==============================================================================
python_rest_engineer = Agent(
    role="Expert Python REST API Integration Engineer",
    goal="Autonomously architect a modular, production-grade Python solution and flash it onto the disk.",
    backstory=(
        "You are an expert systems developer specializing in REST automation. "
        "CRITICAL ARCHITECTURAL AUTONOMY: You reject messy single-file code blocks. You analyze the complexity of the target "
        "FusionCompute endpoints and autonomously design a multi-file layout, determining the optimal number of sub-modules "
        "and their respective filenames (e.g., decoupling session tokens handling, async tasks status polling, and main deployment execution).\n"
        "PIPELINE RULES: You strictly perform your 5-stage sequential lookup before writing files:\n"
        "  1. Run tool 'fetch_all_api_headings' to map out global available API headings scope.\n"
        "  2. Run tool 'read_api_format_specification' to digest protocol rules under 'API接口格式'.\n"
        "  3. Run tool 'read_api_code_blueprints' to analyze native cURL blueprints and inspect exact JSON nesting responses.\n"
        "  4. Run tool 'query_specific_section_content' repeatedly to gather explicit parameter shapes for target actions.\n"
        "  5. Autonomously design the project structure, package code blocks into a dictionary matrix, and invoke "
        "tool 'write_modular_python_files' to flash the entire workspace onto the disk at once.\n"
        "LIFECYCLE CLOSURE: For all asynchronous actions, you ALWAYS implement an explicit polling loop tracking 'taskUrn'.\n"
        "All code comments inside your generated python files MUST be written in English."
    ),
    tools=[
        PythonRestTools.fetch_all_api_headings,
        PythonRestTools.read_api_format_specification,
        PythonRestTools.read_api_code_blueprints,
        PythonRestTools.query_specific_section_content,
        PythonRestTools.write_modular_python_files
    ],
    verbose=True,
    allow_delegation=False,
    llm=coding_llm
)

# ==============================================================================
# ROLE 3: ANSIBLE INFRASTRUCTURE AUTOMATION ENGINEER (SCHEME A ORCHESTRATOR)
# ==============================================================================
ansible_automation_engineer = Agent(
    role="Expert Ansible Playbook Infrastructure Automation Engineer",
    goal="Autonomously structure a clean, decoupled Ansible automation layout and deploy files onto the disk.",
    backstory=(
        "You are a master DevOps orchestration engineer specializing in large-scale data center automation.\n"
        "CRITICAL ARCHITECTURAL AUTONOMY: You reject un-abstracted single-playbook dumps. You autonomously structure your "
        "automation project into logical modular layouts, deciding how to separate main playbooks, environment variable "
        "dictionaries, host inventories, or task snippets into distinct files based on software engineering best practices.\n"
        "PIPELINE RULES: You strictly follow your 8-stage lookup sequence before opening files:\n"
        "  1. Execute tool 'fetch_all_api_headings' and 'fetch_all_ansible_headings' to map global dual headings directories.\n"
        "  2. Execute tool 'read_api_format_specification' and 'read_ansible_module_specification' to digest specifications.\n"
        "  3. Execute tool 'read_api_code_blueprints' and 'read_ansible_code_blueprints' to analyze formatting blueprints.\n"
        "  4. Execute tool 'query_specific_section_content' repeatedly to pull parameters for specific structures.\n"
        "  5. Map your finalized file layout into a dictionary matrix and execute tool 'write_modular_ansible_files' "
        "to flash the entire automation environment onto the disk at once.\n"
        "CRITICAL BUSINESS FALLBACK SKILL: If dedicated native modules are missing or parameter-constrained, instantly activate "
        "your 'fc_generic 终极兜底' strategy by pulling raw REST structures via 'query_specific_section_content' and wrapping them inside 'fc_generic'.\n"
        "LIFECYCLE CLOSURE: You enforce perfect synchronization using async/poll or dedicated task manager modules.\n"
        "All code comments inside your generated automation files MUST be written in English."
    ),
    tools=[
        AnsibleAutomationTools.fetch_all_api_headings,
        AnsibleAutomationTools.fetch_all_ansible_headings,
        AnsibleAutomationTools.read_api_format_specification,
        AnsibleAutomationTools.read_ansible_module_specification,
        AnsibleAutomationTools.read_api_code_blueprints,
        AnsibleAutomationTools.read_ansible_code_blueprints,
        AnsibleAutomationTools.query_specific_section_content,
        AnsibleAutomationTools.write_modular_ansible_files
    ],
    verbose=True,
    allow_delegation=False,
    llm=coding_llm
)

# ==============================================================================
# DYNAMIC DEPLOYMENT MATRIX VERIFICATION RUNNER
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*20 + " AUDITING UNIFIED HYBRID AGENTS ROUTER " + "="*20)
    print(f"  [ROUTING DIALOG] Analyst Target Model : {analyst_llm.model}")
    print(f"  [ROUTING DIALOG] Engineer Target Model: {coding_llm.model}")
    print(f"  Analyst tools  : {len(virtualization_analyst.tools)}")
    print(f"  Python tools   : {len(python_rest_engineer.tools)}")
    print(f"  Ansible tools  : {len(ansible_automation_engineer.tools)}")
    print("="*60 + "\n")