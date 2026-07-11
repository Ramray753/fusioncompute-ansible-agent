import os
import yaml
import logging
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# ==============================================================================
# IMPORT THE NEW PYDANTIC SCHEMA
# ==============================================================================
from crew_schema import BlueprintSchema

# Configure standardized runtime logging metrics before bootstrapping modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Establish absolute project root directory anchor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Bootstrap environment variables
load_dotenv()

# Import the decoupled MCP-enabled multi-agent factory instances securely from the new structure
from crew_agents import (
    ansible_blueprint_designer, 
    ansible_code_engineer, 
    ansible_code_reviewer
)

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


def run_virtualization_orchestrator(user_prompt: str):
    """
    Orchestrates the multi-agent sequential pipeline using synchronized token 
    identifiers and explicit multi-file file-system context handshakes.
    """
    logger.info(f"Initializing multi-agent pipeline orchestration for prompt: '{user_prompt}'")
    
    task_prompts = _load_task_prompt_config()
    
    # ==============================================================================
    # TASK 1: ARCHITECTURAL DESIGN & ROUTING PHASE
    # ==============================================================================
    t_architect = task_prompts["architect_task"]
    architect_task = Task(
        description=t_architect["description"],
        expected_output=t_architect["expected_output"],
        agent=ansible_blueprint_designer,
        # BIND THE SCHEMA HERE: Forces the agent to output strict JSON matching the Pydantic model
        output_pydantic=BlueprintSchema
    )
    logger.info("Task 1 [Architectural Design Block] successfully mapped onto Blueprint Designer Agent with Pydantic constraint.")
    
    # ==============================================================================
    # TASK 2: PRODUCTION CODE COMPILATION PHASE
    # ==============================================================================
    t_coder = task_prompts["coder_task"]
    coder_task = Task(
        description=t_coder["description"],
        expected_output=t_coder["expected_output"],
        agent=ansible_code_engineer,
        # Handshake: The coder now receives a validated Pydantic model dump (JSON) instead of free text
        context=[architect_task]
    )
    logger.info("Task 2 [Code Compilation Block] successfully mapped and bound via context handshake to Task 1.")
    
    # ==============================================================================
    # TASK 3: AUDIT & QUALITY ASSURANCE REVIEW PHASE
    # ==============================================================================
    t_reviewer = task_prompts["reviewer_task"]
    reviewer_task = Task(
        description=t_reviewer["description"],
        expected_output=t_reviewer["expected_output"],
        agent=ansible_code_reviewer,
        context=[architect_task, coder_task]
    )
    logger.info("Task 3 [Static Quality Gate Block] successfully mapped and bound via context handshake to upstream tasks.")
    
    # ==============================================================================
    # PIPELINE CRADLE EXECUTION ENGINE
    # ==============================================================================
    production_crew = Crew(
        agents=[
            ansible_blueprint_designer, 
            ansible_code_engineer, 
            ansible_code_reviewer
        ],
        tasks=[
            architect_task, 
            coder_task, 
            reviewer_task
        ],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info("Launching waterfall orchestrator kickoff engine loop...")
    production_crew.kickoff(inputs={"user_request": user_prompt})
    
    logger.info("Multi-agent sequential pipeline orchestration cascade executed completely.")
    print("\n" + "="*20 + " DEPLOYMENT MATRIX COMPLETE " + "="*20)
    print("  [SUCCESS] Code compilation committed completely. Please check './output_ansible/' directory.")
    print("=" * 68 + "\n")


# ==============================================================================
# PURE INTERACTIVE COMMAND-LINE GATEWAY ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*21 + " FUSIONCOMPUTE AUTOMATION RUNTIME " + "="*21)
    try:
        user_input_requirement = input("[PROMPT] Please enter your automation requirement: ").strip()
        if user_input_requirement:
            run_virtualization_orchestrator(user_input_requirement)
        else:
            print("[FATAL ERROR] Requirement validation failed: Input string cannot be empty.")
    except KeyboardInterrupt:
        print("\n[INFO] Orchestration runtime gateway terminated by user. Exiting safely.")