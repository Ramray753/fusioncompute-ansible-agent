import os
import yaml

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