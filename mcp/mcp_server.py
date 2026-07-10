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

@mcp.resource("fc://ansible/exmaple/single")
def get_ansible_example_single() -> str:
    """Retrieve standard end-to-end single-operation playbook production architectures."""
    return mcp_resources.fetch_ansible_example("single_sections", "Single Operation")

@mcp.resource("fc://ansible/exmaple/sequential")
def get_ansible_example_sequential() -> str:
    """Retrieve single-stream, ordered sequential batch process orchestration playbooks."""
    return mcp_resources.fetch_ansible_example("batch_sequential_sections", "Sequential Batch")

@mcp.resource("fc://ansible/exmaple/parallel")
def get_ansible_example_parallel() -> str:
    """Retrieve multi-stream, high-concurrency parallel automation script templates."""
    return mcp_resources.fetch_ansible_example("batch_parallel_sections", "Parallel Batch")

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
def write_modular_ansible_files(file_matrix: dict) -> str:
    """Physical write transaction creating modular playbook scripts securely inside workspace filesystem."""
    return mcp_tools.write_files_to_workspace(file_matrix)

@mcp.tool()
def read_workspace_playbook_file(file_name: str) -> str:
    """Physical read validation targeting specific workspace files to support compliance auditing."""
    return mcp_tools.read_file_from_workspace(file_name)

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