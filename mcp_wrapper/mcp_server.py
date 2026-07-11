import os
import sys
from mcp.server.fastmcp import FastMCP

# Ensure the 'mcp' subdirectory is prioritized in sys.path for clean local module resolution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import decoupled implementations from individual abstraction layers inside mcp/
import mcp_resources
import mcp_tools
import mcp_prompts

# Initialize FastMCP Server Gateway Instance for Production
mcp = FastMCP("FusionCompute-Context-Server")

# ==============================================================================
# REGISTER MCP RESOURCES (Pure Standard Read-Only Static Vectors)
# ==============================================================================

@mcp.resource("fc://api/headings")
def get_api_headings() -> str:
    """Retrieve the complete technical section headings index of the FusionCompute REST API."""
    return mcp_resources.fetch_api_headings()

@mcp.resource("fc://ansible/example/single")
def get_ansible_example_single() -> str:
    """Retrieve single-operation playbook architectures and their execution logs."""
    return mcp_resources.fetch_ansible_example_single()

@mcp.resource("fc://ansible/example/sequential")
def get_ansible_example_sequential() -> str:
    """Retrieve ordered sequential batch process playbooks and their execution logs."""
    return mcp_resources.fetch_ansible_example_sequential()

@mcp.resource("fc://ansible/example/parallel")
def get_ansible_example_parallel() -> str:
    """Retrieve high-concurrency parallel automation scripts and their execution logs."""
    return mcp_resources.fetch_ansible_example_parallel()

@mcp.resource("fc://api/spec")
def get_api_spec() -> str:
    """Retrieve baseline REST URL layouts, HTTP methods protocol, and formatting standards."""
    return mcp_resources.fetch_global_spec("base_spec_top_level", "fusioncompute_8100_api_cleaned.docx")

@mcp.resource("fc://ansible/spec")
def get_ansible_spec() -> str:
    """Retrieve syntax definitions, execution constraints, and parameters of Ansible modules."""
    return mcp_resources.fetch_global_spec("module_spec_top_level", "fusioncompute_ansible_module_cleaned.docx")

# ==============================================================================
# REGISTER MCP RESOURCE TEMPLATES (Legitimate Dynamic Routing Template)
# ==============================================================================

@mcp.resource("fc://api/content/{keyword}")
def get_specific_api_content(keyword: str) -> str:
    """Dynamic lookup resource pulling specific endpoint body tables by precise Chinese name."""
    return mcp_resources.query_api_content_hybrid(keyword)

# ==============================================================================
# REGISTER MCP TOOLS (Actions with Hardware System Side-Effects)
# ==============================================================================

@mcp.tool()
def initialize_output_dir() -> str:
    """Creates target output directory and copies whitelisted system files. MUST be called first."""
    return mcp_tools.initialize_output_dir()

@mcp.tool()
def write_modular_ansible_files(file_matrix: dict) -> str:
    """Physical write transaction creating modular playbook scripts securely inside workspace filesystem."""
    return mcp_tools.write_files_to_workspace(file_matrix)

@mcp.tool()
def read_workspace_playbook_file(file_name: str) -> str:
    """Physical read validation targeting specific workspace files to support compliance auditing."""
    return mcp_tools.read_file_from_workspace(file_name)

@mcp.tool()
def validate_yaml_jinja_ast(file_name: str) -> str:
    """Physical static analysis to validate YAML and Jinja2 AST compliance."""
    return mcp_tools.validate_yaml_jinja_ast(file_name)

@mcp.tool()
def run_ansible_syntax_check(playbook_name: str) -> str:
    """Native Ansible syntax verification using the local ansible-playbook runtime."""
    return mcp_tools.run_ansible_syntax_check(playbook_name)

# ==============================================================================
# REGISTER MCP PROMPTS (Cascade Multi-Agent Governance Personas)
# ==============================================================================

@mcp.prompt("blueprint-designer")
def prompt_blueprint_designer(user_requirement: str) -> str:
    """Generates structural persona constraints bound safely to static resource URIs."""
    return mcp_prompts.compile_blueprint_designer_prompt(user_requirement)

@mcp.prompt("code-engineer")
def prompt_code_engineer(architect_blueprint: str) -> str:
    """Generates compiler engineering prompts using double-braces escaped schema targets."""
    return mcp_prompts.compile_code_engineer_prompt(architect_blueprint)

@mcp.prompt("code-reviewer")
def prompt_code_reviewer(architect_blueprint: str, compiled_code_manifest: str) -> str:
    """Generates static quality gate auditing prompts to isolate file verification rules."""
    return mcp_prompts.compile_code_reviewer_prompt(architect_blueprint, compiled_code_manifest)

if __name__ == "__main__":
    # Launch stdio routing pipeline engine seamlessly
    mcp.run()