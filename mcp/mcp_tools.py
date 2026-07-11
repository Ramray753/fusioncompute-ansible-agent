import os
import yaml
import subprocess
import re
import jinja2

# Establish absolute project root directory anchor (up two levels from mcp/mcp_tools.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_output_dir() -> str:
    """
    Dynamically loads the target workspace output directory from the centralized 'conf/conf.yaml'.
    Falls back gracefully to an absolute path anchor if the configuration matrix is missing.
    """
    config_file = os.path.join(BASE_DIR, "conf", "conf.yaml")
    if not os.path.exists(config_file):
        config_file = os.path.join(BASE_DIR, "conf", "conf.yml")
        
    default_dir = os.path.join(BASE_DIR, "output_ansible")
    if not os.path.exists(config_file):
        return default_dir
        
    try:
        with open(config_file, "r", encoding="utf-8") as file_handle:
            config_data = yaml.safe_load(file_handle)
            if config_data and "workspace" in config_data:
                configured_path = config_data["workspace"].get("output_dir", "./output_ansible")
                if os.path.isabs(configured_path):
                    return configured_path
                return os.path.abspath(os.path.join(BASE_DIR, configured_path))
            return default_dir
    except Exception:
        return default_dir

def write_files_to_workspace(file_matrix: dict) -> str:
    """Executes physical file matrix deployment to local workspace disk topology securely."""
    output_dir = _load_output_dir()
    try:
        os.makedirs(output_dir, exist_ok=True)
        written_files = []
        
        for file_name, content in file_matrix.items():
            base_name = os.path.basename(file_name)
            if not base_name.endswith(('.yml', '.yaml', '.py', '.conf')):
                continue
                
            file_path = os.path.join(output_dir, base_name)
            with open(file_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(content)
            written_files.append(base_name)
            
        return f"[SUCCESS] Deployed {len(written_files)} files into {output_dir}: {', '.join(written_files)}"
    except Exception as error:
        return f"[IO ERROR] Failed to commit modular files to disk. Details: {str(error)}"

def read_file_from_workspace(file_name: str) -> str:
    """Executes local file read operations from absolute workspace path to support auditing workflows."""
    output_dir = _load_output_dir()
    target_path = os.path.join(output_dir, os.path.basename(file_name))
    
    if not os.path.exists(target_path):
        return f"[IO ERROR] Requested playbook file '{file_name}' does not exist in output directory '{output_dir}'."
        
    try:
        with open(target_path, "r", encoding="utf-8") as file_handle:
            return file_handle.read()
    except Exception as error:
        return f"[IO ERROR] Failed to access source file '{file_name}'. Details: {str(error)}"

def validate_yaml_jinja_ast(file_name: str) -> str:
    """
    Perform physical AST validation for both YAML syntax and Jinja2 expressions.
    Targets files inside the isolated workspace directory.
    """
    output_dir = _load_output_dir()
    target_path = os.path.join(output_dir, os.path.basename(file_name))
    
    if not os.path.exists(target_path):
        return f"[VALIDATION ERROR] File '{file_name}' does not exist in workspace."

    try:
        with open(target_path, "r", encoding="utf-8") as file_handle:
            content = file_handle.read()
            
        # Phase 1: YAML Abstract Syntax Tree parsing
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as yaml_err:
            return f"[YAML SYNTAX ERROR] Failed to parse '{file_name}'.\nDetails: {str(yaml_err)}"

        # Phase 2: Jinja2 Expression parsing
        # Directly parse the entire file content. Jinja2 will naturally find and validate 
        # all {{ }} and {% %} blocks, and immediately catch unclosed tags.
        try:
            env = jinja2.Environment()
            env.parse(content)
        except jinja2.exceptions.TemplateSyntaxError as jinja_err:
            return (f"[JINJA2 SYNTAX ERROR] Failed to parse Jinja2 expression in '{file_name}'.\n"
                    f"Details: {jinja_err.message} (Line {jinja_err.lineno})")

        return f"[SUCCESS] AST validation passed for '{file_name}'."
        
    except Exception as e:
        return f"[SYSTEM ERROR] AST validation failed unexpectedly: {str(e)}"

def run_ansible_syntax_check(playbook_name: str) -> str:
    """
    Execute native ansible-playbook --syntax-check against the target playbook.
    """
    output_dir = _load_output_dir()
    target_path = os.path.join(output_dir, os.path.basename(playbook_name))
    
    if not os.path.exists(target_path):
        return f"[VALIDATION ERROR] Playbook '{playbook_name}' does not exist."

    try:
        # Execute the native command within the subprocess
        result = subprocess.run(
            ["ansible-playbook", "--syntax-check", target_path],
            capture_output=True,
            text=True,
            cwd=output_dir
        )
        
        if result.returncode == 0:
            return f"[SUCCESS] Ansible syntax check passed for '{playbook_name}'.\n{result.stdout.strip()}"
        else:
            return f"[ANSIBLE SYNTAX ERROR] Playbook check failed.\n{result.stderr.strip()}"
            
    except FileNotFoundError:
        return "[SYSTEM ERROR] 'ansible-playbook' command not found. Ensure ansible-core is installed in the environment."
    except Exception as e:
        return f"[SYSTEM ERROR] Subprocess execution failed: {str(e)}"

# ==============================================================================
# UNIT TESTS FOR PHYSICAL VALIDATORS (Self-contained Execution Block)
# ==============================================================================
if __name__ == "__main__":
    def _setup_test_files():
        """Create mock playbooks for validation testing."""
        test_dir = _load_output_dir()
        os.makedirs(test_dir, exist_ok=True)

        valid_yaml = os.path.join(test_dir, "valid_mock.yml")
        invalid_yaml = os.path.join(test_dir, "invalid_yaml_mock.yml")
        invalid_jinja = os.path.join(test_dir, "invalid_jinja_mock.yml")

        with open(valid_yaml, "w", encoding="utf-8") as f:
            f.write("---\n- name: Test playbook\n  hosts: localhost\n  tasks:\n    - name: Print\n      debug:\n        msg: \"{{ 'Hello' }}\"\n")

        with open(invalid_yaml, "w", encoding="utf-8") as f:
            f.write("---\n- name: Broken YAML\n  hosts: localhost\n  tasks:\n  - name: Print\n     debug:\n      msg: Hello\n") # Indentation error

        with open(invalid_jinja, "w", encoding="utf-8") as f:
            f.write("---\n- name: Broken Jinja\n  hosts: localhost\n  tasks:\n    - name: Print\n      debug:\n        msg: \"{{ unclosed_var \"\n")

        # Return just the filenames because the validators use basenames to lookup in output_dir
        return "valid_mock.yml", "invalid_yaml_mock.yml", "invalid_jinja_mock.yml"

    def _run_tests():
        valid_f, invalid_yaml_f, invalid_jinja_f = _setup_test_files()

        print("================ AST VALIDATOR TESTS ================")
        print(f"1. Valid File: {validate_yaml_jinja_ast(valid_f)}")
        print("-" * 40)
        print(f"2. Invalid YAML: {validate_yaml_jinja_ast(invalid_yaml_f)}")
        print("-" * 40)
        print(f"3. Invalid Jinja: {validate_yaml_jinja_ast(invalid_jinja_f)}")
        
        print("\n================ ANSIBLE-PLAYBOOK TESTS ================")
        print(f"1. Valid File: {run_ansible_syntax_check(valid_f)}")
        print("-" * 40)
        print(f"2. Invalid YAML: {run_ansible_syntax_check(invalid_yaml_f)}")

    _run_tests()