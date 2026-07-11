import os
import sys
import yaml
import logging
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# ==============================================================================
# WORKSPACE PATH RESOLUTION & SYS.PATH INJECTION
# ==============================================================================
# Resolve the absolute path of the root directory (one level up from 'test/')
# This ensures Python can find root-level modules and config folders.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Establish absolute project root directory anchor for config loading
BASE_DIR = PROJECT_ROOT

# ==============================================================================
# IMPORT THE NEW PYDANTIC SCHEMA & AGENTS
# ==============================================================================
# Now that PROJECT_ROOT is in sys.path, these imports will succeed
from crew_schema import BlueprintSchema

# NOTE: Ensure your agents file is named 'crew_agents.py' or 'agents.py' as appropriate.
# Since your tree showed 'agents.py', if you hit an import error here, change 'crew_agents' to 'agents'.
from crew_agents import ansible_blueprint_designer

# Configure standardized runtime logging metrics before bootstrapping modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Bootstrap environment variables
load_dotenv()

def _load_task_prompt_config() -> dict:
    """Helper function to load multi-line structural task descriptions from external decoupled configuration matrix."""
    config_file = os.path.join(BASE_DIR, "conf", "tasks.yaml")
    if not os.path.exists(config_file):
        config_file = os.path.join(BASE_DIR, "conf", "tasks.yml")
        
    if not os.path.exists(config_file):
        logger.error(f"Requisite task asset file '{config_file}' is missing from workspace.")
        raise FileNotFoundError(f"[FATAL ERROR] Requisite task asset file '{config_file}' is missing from workspace.")
    
    with open(config_file, "r", encoding="utf-8") as file_handle:
        try:
            return yaml.safe_load(file_handle)
        except Exception as error:
            logger.error(f"Failed to parse structural task configuration file: {config_file}")
            raise ValueError(f"[PARSING ERROR] Failed to load structural task yaml from {config_file}. Details: {str(error)}")

def run_architect_test(user_prompt: str):
    """
    Executes an isolated single-task runtime pipeline to evaluate and verify
    the [Automation Architect]'s structured Pydantic schema generation logic.
    """
    logger.info(f"Initializing isolated architectural design audit for prompt: '{user_prompt}'")
    
    task_prompts = _load_task_prompt_config()
    
    # ==============================================================================
    # ISOLATED TASK: ARCHITECTURAL DESIGN & ROUTING PHASE
    # ==============================================================================
    t_architect = task_prompts["architect_task"]
    isolated_architect_task = Task(
        description=t_architect["description"],
        expected_output=t_architect["expected_output"],
        agent=ansible_blueprint_designer,
        # BIND THE SCHEMA HERE: Forces the agent to output strict JSON matching the Pydantic model
        output_pydantic=BlueprintSchema
    )
    logger.info("Task 1 [Architectural Design Block] successfully mapped onto Blueprint Designer Agent with Pydantic constraint.")
    
    # Construct a lightweight single-agent crew for fast iterative testing
    test_crew = Crew(
        agents=[ansible_blueprint_designer],
        tasks=[isolated_architect_task],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info("Launching isolated agent kickoff engine loop...")
    
    # Kickoff the agent and capture the final architectural schema blueprint
    blueprint_result = test_crew.kickoff(inputs={"user_request": user_prompt})
    
    logger.info("Isolated architect pipeline executed completely.")
    
    # Stream the resulting blueprint directly to the console for engineer inspection
    print("\n" + "="*20 + " [TEST] ARCHITECT BLUEPRINT OUTPUT (JSON) " + "="*20)
    
    # CrewAI automatically parses output_pydantic into the .pydantic attribute
    if hasattr(blueprint_result, 'pydantic') and blueprint_result.pydantic:
        # Dump the Pydantic model back to formatted JSON for beautiful CLI output
        formatted_json = blueprint_result.pydantic.model_dump_json(indent=4)
        print(formatted_json)
    else:
        # Fallback if CrewAI failed to map it to the attribute but returned raw text
        print(blueprint_result.raw)
        
    print("="*82 + "\n")

# ==============================================================================
# PURE INTERACTIVE COMMAND-LINE GATEWAY ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*21 + " FUSIONCOMPUTE ARCHITECT VERIFIER " + "="*21)
    try:
        # Prompt the engineer for the specific virtualization orchestration scenario
        user_input_requirement = input("[PROMPT] Enter automation requirement to test design: ").strip()
        if user_input_requirement:
            run_architect_test(user_input_requirement)
        else:
            print("[FATAL ERROR] Requirement validation failed: Input string cannot be empty.")
    except KeyboardInterrupt:
        print("\n[INFO] Orchestration runtime gateway terminated by user. Exiting safely.")