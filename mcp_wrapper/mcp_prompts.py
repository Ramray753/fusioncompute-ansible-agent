import os
import yaml

# Establish absolute project root directory anchor
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _get_agent_persona(agent_key: str) -> dict:
    """Helper function to safely extract agent blocks from the configuration file."""
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

def _dict_to_xml(data, indent_level: int = 1) -> str:
    """
    Recursively converts a dictionary or list into an XML formatted string.
    Dynamically generates XML tags based on dictionary keys.
    """
    indent = "  " * indent_level
    inner_indent = "  " * (indent_level + 1)
    
    if isinstance(data, dict):
        xml_parts = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                inner_content = _dict_to_xml(value, indent_level + 1)
                xml_parts.append(f"{indent}<{key}>\n{inner_content}\n{indent}</{key}>")
            else:
                # Handle multiline strings securely by applying uniform indentation
                lines = str(value).strip().split('\n')
                formatted_lines = "\n".join(f"{inner_indent}{line}" for line in lines)
                xml_parts.append(f"{indent}<{key}>\n{formatted_lines}\n{indent}</{key}>")
        return "\n".join(xml_parts)
        
    elif isinstance(data, list):
        xml_parts = []
        for item in data:
            if isinstance(item, (dict, list)):
                inner_content = _dict_to_xml(item, indent_level + 1)
                xml_parts.append(f"{indent}<item>\n{inner_content}\n{indent}</item>")
            else:
                lines = str(item).strip().split('\n')
                formatted_lines = "\n".join(f"{inner_indent}{line}" for line in lines)
                xml_parts.append(f"{indent}<item>\n{formatted_lines}\n{indent}</item>")
        return "\n".join(xml_parts)
        
    else:
        return str(data)

def compile_blueprint_designer_prompt(user_requirement: str) -> str:
    """Compiles architect guidelines into a dynamic XML structure for LLM parsing."""
    persona_dict = _get_agent_persona("ansible_blueprint_designer")
    system_instructions = _dict_to_xml(persona_dict, indent_level=1)
    
    return f"""<system_instructions>
{system_instructions}
</system_instructions>

<task_inputs>
  <user_requirement>
{_dict_to_xml(user_requirement, indent_level=2)}
  </user_requirement>
</task_inputs>"""

def compile_code_engineer_prompt(architect_blueprint: str) -> str:
    """Compiles engineering guidelines into a dynamic XML structure for LLM parsing."""
    persona_dict = _get_agent_persona("ansible_code_engineer")
    system_instructions = _dict_to_xml(persona_dict, indent_level=1)
    
    return f"""<system_instructions>
{system_instructions}
</system_instructions>

<task_inputs>
  <architect_blueprint>
{_dict_to_xml(architect_blueprint, indent_level=2)}
  </architect_blueprint>
</task_inputs>"""

def compile_code_reviewer_prompt(architect_blueprint: str, compiled_code_manifest: str) -> str:
    """Compiles static quality assurance guidelines into a dynamic XML structure for LLM parsing."""
    persona_dict = _get_agent_persona("ansible_code_reviewer")
    system_instructions = _dict_to_xml(persona_dict, indent_level=1)
    
    return f"""<system_instructions>
{system_instructions}
</system_instructions>

<task_inputs>
  <architect_blueprint>
{_dict_to_xml(architect_blueprint, indent_level=2)}
  </architect_blueprint>
  
  <compiled_code_manifest>
{_dict_to_xml(compiled_code_manifest, indent_level=2)}
  </compiled_code_manifest>
</task_inputs>"""

# ==============================================================================
# UNIT TESTS FOR DYNAMIC XML PROMPT GENERATION
# ==============================================================================
if __name__ == "__main__":
    print("================ STARTING DYNAMIC XML COMPILATION TESTS ================")
    
    try:
        # Test 1: Blueprint Designer Output
        print("\n[TEST 1] Testing Blueprint Designer Prompt Generation...")
        mock_user_req = "Please configure a sequential batch loop to deploy VMs."
        out_designer = compile_blueprint_designer_prompt(mock_user_req)
        # Print a truncated preview to verify formatting
        print(out_designer[:600] + "\n\n... [TRUNCATED] ...\n")
        print("[TEST 1 SUCCESS]")
        print("-" * 60)
        
        # Test 2: Code Engineer Output
        print("\n[TEST 2] Testing Code Engineer Prompt Generation...")
        mock_blueprint = "### BY: [Automation Architect]\nSelected API: 查询指定主机"
        out_engineer = compile_code_engineer_prompt(mock_blueprint)
        print(out_engineer[:600] + "\n\n... [TRUNCATED] ...\n")
        print("[TEST 2 SUCCESS]")
        print("-" * 60)
        
        # Test 3: Code Reviewer Output
        print("\n[TEST 3] Testing Code Reviewer Prompt Generation...")
        mock_manifest = "### File: main.yml\n---\n- hosts: localhost\n  tasks:\n    - name: '[Task 1.1] Demo'"
        out_reviewer = compile_code_reviewer_prompt(mock_blueprint, mock_manifest)
        print(out_reviewer[:600] + "\n\n... [TRUNCATED] ...\n")
        print("[TEST 3 SUCCESS]")
        print("================ ALL TESTS PASSED SUCCESSFULLY ================")
        
    except FileNotFoundError as err:
        print(f"\n[TEST ENVIRONMENT ERROR] {err}")
        print("Please ensure that 'conf/agents.yaml' exists in the root directory before running this standalone test.")
    except Exception as err:
        print(f"\n[TEST EXECUTION ERROR] An unexpected error occurred: {err}")