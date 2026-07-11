import os
import yaml

# Establish absolute project root directory anchor (up two levels from mcp/mcp_prompts.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _get_agent_persona(agent_key: str) -> dict:
    """Helper function to safely extract agent blocks from the absolute conf/agents.yaml file."""
    config_file = os.path.join(BASE_DIR, "conf", "agents.yaml")
    if not os.path.exists(config_file):
        config_file = os.path.join(BASE_DIR, "conf", "agents.yml")
        
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"[FATAL ERROR] Prompt configuration profile '{config_file}' is missing from workspace.")
        
    with open(config_file, "r", encoding="utf-8") as file:
        try:
            return yaml.safe_load(file)[agent_key]
        except Exception as error:
            raise ValueError(f"[PARSING ERROR] Failed to load YAML context from {config_file}. Details: {str(error)}")

def compile_blueprint_designer_prompt(user_requirement: str) -> str:
    """Injects requirements into multi-file virtualization architect guidelines."""
    designer = _get_agent_persona("ansible_blueprint_designer")
    return f"""
Role: {designer['role']}
Goal: {designer['goal']}
Backstory: {designer['backstory']}

Current Task Requirement:
{user_requirement}

Instructions: You must rely on the following standard protocol URIs to gather required knowledge blocks:
- fc://api/headings (To discover available capabilities and plan workflows)
- fc://ansible/spec (To examine specific module syntax constraints)
- fc://ansible/exmaple/single (To analyze standard playbook layouts and response layer navigations)
- fc://ansible/exmaple/sequential (Strictly reference this IF the requirement mandates ordered, single-stream sequential file loops)
- fc://ansible/exmaple/parallel (Strictly reference this IF the requirement mandates high-concurrency, multi-stream parallel batch processing)
- fc://api/content/{{keyword}} (To discover inputs fields and deduce prerequisite lookup query tasks for identified candidate endpoints)
"""

def compile_code_engineer_prompt(architect_blueprint: str) -> str:
    """Injects the design blueprint into compiled playbook engineering guidelines."""
    engineer = _get_agent_persona("ansible_code_engineer")
    return f"""
Role: {engineer['role']}
Goal: {engineer['goal']}
Backstory: {engineer['backstory']}

Architect Blueprint Inputs (Your Single Source of Truth):
{architect_blueprint}

Instructions: You must leverage the following standard protocol URIs to resolve parameter definitions and immune syntax schemas before using file deployment tools:
- fc://ansible/spec (To evaluate internal FusionCompute Ansible module mechanisms and rules)
- fc://api/spec (To parse global API protocol structures, definitions, and object ID layouts)
- fc://ansible/exmaple/single (To ensure exact adherence to standard layouts and wrapper navigations)
- fc://ansible/exmaple/sequential (Reference this if the architect's blueprint dictates ordered, sequential batch script requirements)
- fc://ansible/exmaple/parallel (Reference this if the architect's blueprint dictates high-concurrency, parallel batch loops)
- fc://api/content/{{keyword}} (To retrieve targeted parameter tables, query params, and body payload structures by providing exact Chinese name)
"""

def compile_code_reviewer_prompt(architect_blueprint: str, compiled_code_manifest: str) -> str:
    """Injects structural code manifests into static compliance quality assurance guidelines."""
    reviewer = _get_agent_persona("ansible_code_reviewer")
    return f"""
Role: {reviewer['role']}
Goal: {reviewer['goal']}
Backstory: {reviewer['backstory']}

Architect Blueprint Reference:
{architect_blueprint}

Compiled Playbook Source Code to Audit:
{compiled_code_manifest}

Instructions: You must execute your audit in TWO STRICT PHASES:

[PHASE 1] Execute Physical Validation Tools FIRST:
- You MUST call 'validate_yaml_jinja_ast' and 'run_ansible_syntax_check' on target files. 
- EXCEPTION: You must completely skip and ignore 'wait_fc_system_task.yml' in your entire workflow.
- Do not proceed until these physical CLI tools return [SUCCESS].

[PHASE 2] Cross-reference API Semantic Rules ONLY when Phase 1 is [SUCCESS]:
- fc://ansible/spec (To verify that module blocks align perfectly with framework expectations)
- fc://api/spec (To check URL sanitization, variables cleanliness, and relative path structures)
- fc://api/content/{{keyword}} (To verify parameter completeness, mandatory body fields, and nested response navigations)

If you find defects in either phase, fix them, call 'write_modular_ansible_files', and IMMEDIATELY RESTART [PHASE 1].
"""