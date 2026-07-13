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
    get_role_based_read_tools,
    initialize_output_dir,
    write_modular_ansible_files,
    read_workspace_playbook_file,
    validate_yaml_jinja_ast,
    run_ansible_syntax_check
)

def _load_and_render_agent_prompt_config(script_type: int) -> dict:
    """Helper function to load and dynamically render multi-line structural agent personas from YAML matrix."""
    config_file = os.path.join(BASE_DIR, "conf", "agents.yaml")
    if not os.path.exists(config_file):
        config_file = os.path.join(BASE_DIR, "conf", "agents.yml")
        
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"[FATAL ERROR] Requisite prompt asset file '{config_file}' is missing from workspace.")
    
    # 1. Dynamically configure instruction strings based on routing type
    batch_instruction = "4. NO BATCH OPERATIONS ALLOWED: Do not build any multi-resource batch execution logic. Looping orchestrations and concurrency paradigms are strictly prohibited."
    example_mcp = ""
    
    if script_type == 2:
        batch_instruction = (
            "4. SEQUENTIAL BATCH OPERATIONS: You MUST read the MCP resource 'fc://ansible/example/sequential' exactly once. Deeply analyze its looping orchestrations and closely mimic its multi-file topology design. Crucially, the detailed execution block running for each sequenced resource item must be isolated into a separate standalone YAML task file, matching the pattern in the example script."
        )
        example_mcp = "- fc://ansible/example/sequential"
    elif script_type == 3:
        batch_instruction = (
            "4. PARALLEL BATCH OPERATIONS: You MUST read the MCP resource 'fc://ansible/example/parallel' exactly once. Deeply analyze its concurrency paradigms and closely mimic its multi-file topology design. Crucially, the detailed execution block running for each concurrent resource item must be isolated into a separate standalone YAML task file, matching the pattern in the example script."
        )
        example_mcp = "- fc://ansible/example/parallel"
        
    # 2. Read raw text and securely inject instructions
    with open(config_file, "r", encoding="utf-8") as file_handle:
        try:
            raw_yaml_str = file_handle.read()
            
            # Using .replace() instead of .format() to avoid KeyError with native YAML curly braces
            rendered_yaml_str = raw_yaml_str.replace("{batch_workflow_instruction}", batch_instruction)
            rendered_yaml_str = rendered_yaml_str.replace("{available_example_mcp}", example_mcp)
            
            return yaml.safe_load(rendered_yaml_str)
        except Exception as error:
            raise ValueError(f"[PARSING ERROR] Failed to load structural yaml context. Details: {str(error)}")

def build_xml_backstory(agent_config: dict) -> str:
    """Extracts granular configuration keys and renders them dynamically into an XML-formatted backstory string."""
    dynamic_keys = {k: v for k, v in agent_config.items() if k not in ["role", "goal"]}
    return _dict_to_xml(dynamic_keys, indent_level=1)

def create_agents(script_type: int):
    """
    Factory function to dynamically instantiate the decoupled multi-agent workforce.
    Injects specific tools and rendering instructions strictly bound to the script_type route.
    """
    # Load fully decoupled and dynamically rendered prompt configurations
    agent_prompts = _load_and_render_agent_prompt_config(script_type)
    
    # Instantiate role-based physical access tools securely configured for this route
    designer_read_tool, engineer_read_tool, reviewer_read_tool = get_role_based_read_tools(script_type)

    # ==============================================================================
    # AGENT 1: BLUEPRINT ARCHITECTURE DESIGNER ([Automation Architect])
    # ==============================================================================
    p_designer = agent_prompts["ansible_blueprint_designer"]
    ansible_blueprint_designer = Agent(
        role=p_designer["role"],
        goal=p_designer["goal"],
        backstory=build_xml_backstory(p_designer),
        tools=[designer_read_tool],
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
            engineer_read_tool, 
            initialize_output_dir,
            write_modular_ansible_files,
            # Add validation tools to empower Agent 2 with internal syntax self-checks
            validate_yaml_jinja_ast, 
            run_ansible_syntax_check
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
            reviewer_read_tool, 
            read_workspace_playbook_file
        ], 
        verbose=True,
        allow_delegation=False,
        llm=agent_llm
    )
    
    # ==============================================================================
    # MUST RETURN THE AGENTS TO THE CALLER
    # ==============================================================================
    return ansible_blueprint_designer, ansible_code_engineer, ansible_code_reviewer