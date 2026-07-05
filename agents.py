import os
from crewai import Agent, LLM

# Import the refactored toolkits with scheme-A multi-file capabilities
from tools_python import PythonRestTools
from tools_ansible import AnsibleAutomationTools

# Configure local open-source LLM container via native CrewAI LLM class
local_llm = LLM(
    model="ollama/qwen2.5:14b", 
    base_url="http://127.0.0.1:11434"
)

# ==============================================================================
# ROLE 1: VIRTUALIZATION REQUIREMENTS ANALYST
# ==============================================================================
virtualization_analyst = Agent(
    role="Huawei FusionCompute Cloud Architect & Requirements Analyst",
    goal="Deconstruct ambiguous infrastructure requests and determine the absolute optimal technical automation route.",
    backstory=(
        "You are a master virtualization infrastructure architect at Huawei. "
        "Your task is to analyze user requests and explicitly choose the execution path: output 'TRACK: PYTHON_REST' "
        "or 'TRACK: ANSIBLE_PLAYBOOK'. You break down tasks into logical steps but never write file outputs directly."
    ),
    verbose=True,
    allow_delegation=False,
    llm=local_llm
)

# ==============================================================================
# ROLE 2: PURE PYTHON REST AUTOMATION ENGINEER (SCHEME A UPGRADE)
# ==============================================================================
python_rest_engineer = Agent(
    role="Expert Python REST API Integration Engineer",
    goal="Autonomously architect a modular, production-grade Python solution and flash it onto the disk.",
    backstory=(
        "You are an expert systems developer specializing in REST automation. "
        "CRITICAL ARCHITECTURAL AUTONOMY: You do not bundle your code into a single massive file. Instead, you analyze "
        "the complexity of the target FusionCompute endpoints and autonomously design a multi-file layout. You have "
        "the absolute freedom to decide the optimal number of sub-modules and their respective filenames (e.g., separating "
        "session logic, error handling, or asynchronous tracking loops into separate files).\n"
        "PIPELINE RULES: You strictly perform your 4-stage sequential lookup (Tool 1 -> Tool 2 -> Tool 3 -> Tool 4). "
        "Once your engineering layout is decided and code blocks are designed, you MUST package them into a dictionary "
        "and invoke Tool 5 ('Write Modular Python Project Files') to flash your entire project onto the disk at once."
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
    llm=local_llm
)

# ==============================================================================
# ROLE 3: ANSIBLE INFRASTRUCTURE AUTOMATION ENGINEER (SCHEME A UPGRADE)
# ==============================================================================
ansible_automation_engineer = Agent(
    role="Expert Ansible Playbook Infrastructure Automation Engineer",
    goal="Autonomously structure a clean, decoupled Ansible automation layout and deploy files onto the disk.",
    backstory=(
        "You are a master DevOps orchestration engineer specializing in large-scale data center automation.\n"
        "CRITICAL ARCHITECTURAL AUTONOMY: You reject messy, un-abstracted single-playbook dumps. You autonomously structure "
        "your automation project into logical modular layouts. You determine the optimal file separation strategy—deciding "
        "exactly how to split main playbooks, environment variable dictionaries, host inventories, or task snippets into "
        "independent files, naming them logically based on software engineering principles.\n"
        "PIPELINE RULES: You strictly follow your 6-stage lookup sequence before opening files. If specialized modules are missing, "
        "you execute the 'fc_generic 终极兜底' skill by pulling REST fields via Tool 7. Finally, you MUST map your finalized "
        "files into a flat dictionary matrix and execute Tool 8 ('Write Modular Playbook Project Files') to flash the "
        "entire automation environment onto the disk at once."
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
    llm=local_llm
)

# ==============================================================================
# AGENT PERSONALITY, ISOLATION & TOOL QUANTITY UNIT TEST
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*20 + " AUDITING UPGRADED SCHEME-A AGENTS MATRICES " + "="*20)

    # Sanity check Tool counts for both engineers
    print(f"\n[CHECK 1] Python Rest Engineer tools count: {len(python_rest_engineer.tools)}")
    print(f"          Registered names: {[t.name for t in python_rest_engineer.tools]}")
    assert len(python_rest_engineer.tools) == 5, "Error: Python engineer must possess exactly 5 tools under Scheme A."

    print(f"\n[CHECK 2] Ansible Engineer tools count: {len(ansible_automation_engineer.tools)}")
    print(f"          Registered names: {[t.name for t in ansible_automation_engineer.tools]}")
    assert len(ansible_automation_engineer.tools) == 8, "Error: Ansible engineer must possess exactly 8 tools under Scheme A."

    print("\n" + "="*23 + " SCHEME-A AGENTS SPECIFICATION ALL GREEN " + "="*23 + "\n")