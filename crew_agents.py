import os
import sys
import yaml
from crewai import Agent

# Ensure the project root is in sys.path to resolve internal modules securely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mcp_wrapper.mcp_prompts import _dict_to_xml
from crew_llm import agent_llm
from crew_tool import (
    designer_read_mcp_resource,
    engineer_read_mcp_resource,
    reviewer_read_mcp_resource,
    initialize_output_dir,
    write_modular_ansible_files,
    read_workspace_playbook_file,
    validate_yaml_jinja_ast,
    run_ansible_syntax_check
)

def _load_agent_prompt_config() -> dict:
    """Helper function to load multi-line structural agent personas from YAML matrix."""
    config_file = os.path.join(BASE_DIR, "conf", "agents.yaml")
    if not os.path.exists(config_file):
        config_file = os.path.join(BASE_DIR, "conf", "agents.yml")
        
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"[FATAL ERROR] Requisite prompt asset file '{config_file}' is missing from workspace.")
    
    with open(config_file, "r", encoding="utf-8") as file_handle:
        try:
            return yaml.safe_load(file_handle)
        except Exception as error:
            raise ValueError(f"[PARSING ERROR] Failed to load structural yaml context. Details: {str(error)}")

def build_xml_backstory(agent_config: dict) -> str:
    """Extracts granular configuration keys and renders them dynamically into an XML-formatted backstory string."""
    dynamic_keys = {k: v for k, v in agent_config.items() if k not in ["role", "goal"]}
    return _dict_to_xml(dynamic_keys, indent_level=1)

# Load fully decoupled prompt configurations from local storage matrix
agent_prompts = _load_agent_prompt_config()

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
    llm=agent_llm
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
    llm=agent_llm
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
    llm=agent_llm
)