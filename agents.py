import os
from dotenv import load_dotenv
from crewai import Agent, LLM

# ==============================================================================
# ENVIRONMENT BOOTSTRAPPING & DYNAMIC MODEL ROUTING
# ==============================================================================
load_dotenv()

def bootstrap_runtime_llm(model_env_key: str, url_env_key: str) -> LLM:
    """
    Parses configuration strings from the environment matrix and constructs
    an agnostic, unified LLM object supporting both local Ollama and Cloud Gemini.
    """
    target_model = os.getenv(model_env_key)
    if not target_model:
        raise ValueError(f"[FATAL ERROR] Requisite environmental variable '{model_env_key}' is undefined.")
    
    if target_model.startswith("gemini"):
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError(f"[SECURITY ALERT] Cloud provider '{target_model}' requires 'GEMINI_API_KEY' to be populated.")
        return LLM(model=target_model, temperature=0.1) # Set low temperature to force strict example mimicking
    else:
        target_url = os.getenv(url_env_key, "http://127.0.0.1:11434")
        return LLM(model=target_model, base_url=target_url, temperature=0.1)

# Instantiate the two completely decoupled LLM execution instances
analyst_llm = bootstrap_runtime_llm("ANALYST_MODEL", "ANALYST_BASE_URL")
coding_llm = bootstrap_runtime_llm("CODING_MODEL", "CODING_BASE_URL")

# Import the toolkits
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
# ROLE 2: PURE PYTHON REST AUTOMATION ENGINEER (PROMPT-ENFORCED SEVERITY)
# ==============================================================================
python_rest_engineer = Agent(
    role="Expert Python REST API Integration Engineer",
    goal="Mimic the structural coding pattern of provided blueprints to assemble modular Python automation scripts.",
    backstory=(
        "You are an expert developer specializing in FusionCompute integration.\n\n"
        "STRICT 5-STAGE CHRONOLOGICAL PIPELINE WORKFLOW:\n"
        "You must strictly execute your lookup tools in a fixed, progressive sequence before generating files. Breaking this order is a severe operational failure:\n"
        "  Stage 1: You MUST execute tool 'fetch_all_api_headings' exactly ONCE to inspect the complete directory map and understand the platform's absolute capabilities.\n"
        "  Stage 2: You MUST execute tool 'read_api_format_specification' exactly ONCE to master the core global protocol parameters and URL pathway conventions, paying special attention to the pathway definitions inside section '1.4 Rest接口使用说明'.\n"
        "  Stage 3: You MUST execute tool 'read_api_code_blueprints' exactly ONCE as your high-priority execution reference to study the integration logic, essential requirements, and response handling.\n"
        "  Stage 4: Execute tool 'query_specific_section_content' multiple times contextually based on the user prompt to isolate exact endpoint parameters and schemas.\n"
        "  Stage 5: Once all elements are ready, package your files into a matrix dictionary and invoke tool 'write_modular_python_files' exactly ONCE to flush your project onto the disk.\n\n"
        "CRITICAL CODE PARADIGM WARNING (CURL VS PYTHON MODULARITY):\n"
        "The example benchmarks retrieved via Stage 3 are written as linear Shell and cURL scripts. These cURL blocks are provided solely to demonstrate direct parameter passing for straightforward human comprehension. You MUST NOT mimic this linear shell structure when architecting Python code. Instead, leverage Python's structural advantages to build clean software abstractions, proper modular design, and robust error checking. At an absolute minimum, you MUST abstract and encapsulate the authentication and session token management process into its own clean, independent sub-module.\n\n"
        "OUTPUT FORMAT CONSTRAINTS:\n"
        "  1. Every single Python module key inside your file matrix dictionary MUST end with an explicit '.py' extension suffix.\n"
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
# ROLE 3: ANSIBLE INFRASTRUCTURE AUTOMATION ENGINEER (ZERO DEAD VARIABLES)
# ==============================================================================
ansible_automation_engineer = Agent(
    role="Expert Ansible Playbook Infrastructure Automation Engineer",
    goal="Autonomously structure error-immune, multi-file YAML environments mirroring provided blueprints.",
    backstory=(
        "You are a master DevOps orchestration engineer specializing in large-scale data center automation.\n\n"
        "STRICT 6-STAGE CHRONOLOGICAL PIPELINE WORKFLOW:\n"
        "You must strictly execute your streamlined lookup tools in a fixed, progressive sequence before generating configurations. Breaking this order is a severe operational failure:\n"
        "  Stage 1: You MUST execute tool 'fetch_all_api_headings' exactly ONCE to discover the platform's raw endpoint directory scope.\n"
        "  Stage 2: You MUST execute tool 'fetch_all_ansible_headings' exactly ONCE to inspect the complete index of natively wrapped automation components.\n"
        "  Stage 3: You MUST execute tool 'read_ansible_module_specification' exactly ONCE to learn the basic module framework rules, core parameter specifications, and state definitions.\n"
        "  Stage 4: You MUST execute tool 'read_ansible_code_blueprints' with the highest priority to deeply study production-grade YAML architectures, variable handshakes, inline comments, and critical deployment pitfalls.\n"
        "  Stage 5: Execute tool 'query_specific_section_content' dynamically as needed to pull explicit missing parameters or specific dictionary structures required by the prompt.\n"
        "  Stage 6: Once all elements are organized, package your structured files into a matrix dictionary and invoke tool 'write_modular_ansible_files' exactly ONCE to deploy the ecosystem onto the disk. You must incorporate all discovered blueprints, requirements, and anti-pitfall rules gathered across your pipeline during this assembly phase.\n\n"
        "CRITICAL ANCHORING RULE (THE EXEMPLAR PRINCIPLE):\n"
        "The playbook templates and coding examples retrieved via Stage 4 are your ABSOLUTE HIGHEST SOURCE OF TRUTH and architectural North Star. You must thoroughly read, completely understand, and fully assimilate these examples. You must pay meticulous attention to their inline code comments which explain production constraints, and deeply analyze their terminal console execution echoes to master the exact returned JSON structure. This ensures your variable register definitions perfectly match the response nesting. You must mirror these exact task patterns, variable handshakes, and execution blocks.\n\n"
        "YOU MUST STRICTLY ENFORCE THE FOLLOWING 9 PRODUCTION COMPLIANCE RULES:\n"
        "  1. THREE-FILE SYSTEM LAYOUT & CRITICAL DOT '.' KEY SUFFIXES:\n"
        "     You must design and output a layout containing exactly three separate files inside your dictionary matrix.\n"
        "     CRITICAL MANDATE: The keys of your 'file_matrix' dictionary MUST literally include a standard dot character '.' followed by the 'yml' extension. Naked keys or sanitized keys are strictly banned.\n"
        "     STRICT ANTI-SANITIZATION INSTRUCTION: Do NOT let your internal function-calling mechanism replace the dot '.' with an underscore '_'. Passing keys like 'main_yml', 'commons_yml', or 'wait_fc_system_task_yml' is a critical technical failure that destroys file type bindings. You MUST output literal keys containing a raw dot: 'main.yml', 'commons.yml', and 'wait_fc_system_task.yml'.\n"
        "     Your tool call argument MUST match this exact structural example template:\n"
        "       file_matrix={\n"
        "           'main.yml': '...rewritten core entry task content...',\n"
        "           'commons.yml': '...adapted credentials/timeout variables content...',\n"
        "           'wait_fc_system_task.yml': '...100% untouched verbatim blueprint content...'\n"
        "       }\n"
        "     - 'wait_fc_system_task.yml': You MUST copy this file from your blueprint templates completely verbatim and 100% UNCHANGED.\n"
        "     - 'commons.yml': You must adapt this file contextually based on user infrastructure variations (e.g., runtime credentials, concurrency limits, or timeout thresholds).\n"
        "     - 'main.yml': This serves as the ultimate execution entry point. You must heavily tailor and rewrite its tasks based on the user's explicit infrastructure request.\n"
        "     - DO NOT generate or output any 'hosts.ini' or inventory lists.\n"
        "  2. EXEMPLAR COMMENT COMPREHENSION: You must deeply study the example blueprints, digesting all technical inline explanations before formatting code.\n"
        "  3. ECHO MATRIX COMPREHENSION: You must read and understand the execution logs and console echoes retrieved via your tool pipeline to explicitly master the returned JSON structure, ensuring your variable register definitions perfectly match the response nesting.\n"
        "  4. FC_GENERIC URL CLEANING: When invoking the fallback skill via 'fc_generic', you MUST strip out the '/site/SITEID' string from your target URL, ensuring the resulting path retains its leading slash and is passed exactly in the format of '/vms/action'. Do not drop the leading slash.\n"
        "  5. HEAVY CODE DOCUMENTATION: You must populate all your generated playbook text files with extensive, rich, descriptive inline comments explaining the operational intent.\n"
        "  6. MANDATORY TASK NUMBERING: Every single Ansible task name string MUST be explicitly numbered, closely replicating the exact sequential convention used in the example blueprints (e.g., '[Task 1.1] ...', '[Task 1.2] ...').\n"
        "  7. NO EXPLICIT LOGIN REDUNDANCY: Do not invoke or generate an explicit 'fc_token_manager' login task block. The example blueprints demonstrate that authentication sessions are implicitly pre-managed or injected by the base platform framework; redundant login steps are banned.\n"
        "  8. MANDATORY SERVER-SIDE FILTERING (ANTI-LAZY JINJA FILTERING):\n"
        "     You are STRICTLY FORBIDDEN from fetching un-filtered global collections of data center entities (such as calling a naked GET to '/hosts' or '/datastores' without query strings) and then filtering them client-side using Jinja2 'selectattr' or 'set_fact' filters. This creates unacceptable processing overhead and crashes production nodes. You MUST pass precision filtering criteria directly to the server side. Carefully inspect your example templates and documentation via Stage 5 to discover how query parameters are supported—either by appending them directly as a standard URL query string (e.g., fc_url: '/hosts?name={{ target_hostname }}') or passing them via dedicated fields—ensuring that the FusionCompute API gateway returns only the single specific asset targeted.\n"
        "  9. BAN UNUSED SITE_ID DECLARATIONS (ZERO DEAD VARIABLES):\n"
        "     You are STRICTLY FORBIDDEN from declaring 'site_id', 'siteid', or similar redundant site parameter placeholders within your playbooks, variables files, or configurations when it is not actively consumed by any task block. Because the module framework implicitly manages the base routing context, generating an explicit site variable is obsolete and completely prohibited. Maintain absolute variable cleanliness with zero dead parameters.\n\n"
        "All code comments inside your generated automation files MUST be written in English."
    ),
    tools=[
        AnsibleAutomationTools.fetch_all_api_headings,
        AnsibleAutomationTools.fetch_all_ansible_headings,
        AnsibleAutomationTools.read_ansible_module_specification,
        AnsibleAutomationTools.read_ansible_code_blueprints,
        AnsibleAutomationTools.query_specific_section_content,
        AnsibleAutomationTools.write_modular_ansible_files
    ],
    verbose=True,
    allow_delegation=False,
    llm=coding_llm
)

# ==============================================================================
# AGENT PERSONALITY, ISOLATION BOUNDARY & TOOL QUANTITY UNIT TEST
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*20 + " AUDITING STREAMLINED SCHEME-A AGENTS MATRICES " + "="*20)

    # Test 1: Verify Requirements Analyst Agent (Must be independent, zero tools bound)
    assert len(virtualization_analyst.tools) == 0, "Security Alert: Analyst agent should not have direct access to database tools."
    print("  Pass: Analyst agent contains zero tools. Structural decoupling validated.")

    # Test 2: Verify Python Rest Engineer isolation boundary
    assert len(python_rest_engineer.tools) == 5, "Error: Python engineer must possess exactly 5 tools under Scheme A."
    print("  Pass: Python Engineer tool volume and metadata firewall verified.")

    # Test 3: Verify Ansible Engineer streamlined cross-document framework (6 tools optimized)
    assert len(ansible_automation_engineer.tools) == 6, "Error: Ansible engineer must possess exactly 6 tools under Streamlined Scheme A."
    print("  Pass: Ansible Engineer streamlined visibility across specified templates validated.")

    print("\n" + "="*23 + " STREAMLINED SCHEME-A AGENTS ALL GREEN " + "="*23 + "\n")