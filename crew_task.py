import os
import yaml
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# ==============================================================================
# IMPORT CENTRALIZED LOGGER & SCHEMAS
# ==============================================================================
# Importing logger from our centralized logging module
from crew_log import logger
# Re-imported ReviewSchema to enforce JSON structure on Agent 3
from crew_schema import BlueprintSchema, ReviewSchema
from crew_agents import create_agents

# Establish absolute project root directory anchor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Bootstrap environment variables (e.g., API keys)
load_dotenv()

def _load_task_prompt_config() -> dict:
    """Helper function to load generic structural task descriptions."""
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

# ==============================================================================
# SINGLE CREW 4-STEP PIPELINE ORCHESTRATOR
# ==============================================================================
def run_virtualization_orchestrator(user_prompt: str, script_type: int):
    """
    Executes a streamlined, purely sequential 4-step pipeline.
    Relies natively on LLM context passing and implicit control flow.
    """
    logger.info(f"Initializing 4-Step Pipeline orchestration for route: {script_type}")
    
    # Initialize dynamic factories and prompts
    designer, engineer, reviewer = create_agents(script_type)
    task_prompts = _load_task_prompt_config()

    # --------------------------------------------------------------------------
    # TASK 1: ARCHITECTURAL DESIGN
    # --------------------------------------------------------------------------
    t_architect = task_prompts["architect_task"]
    architect_task = Task(
        description=t_architect["description"].replace("{user_request}", user_prompt),
        expected_output=t_architect["expected_output"],
        agent=designer,
        output_json=BlueprintSchema
    )
    
    # --------------------------------------------------------------------------
    # TASK 2: INITIAL CODE COMPILATION
    # --------------------------------------------------------------------------
    t_coder = task_prompts["coder_task"]
    coder_task = Task(
        description=t_coder["description"],
        expected_output=t_coder["expected_output"],
        agent=engineer,
        context=[architect_task]
    )
    
    # --------------------------------------------------------------------------
    # TASK 3: AUDIT & QUALITY ASSURANCE
    # --------------------------------------------------------------------------
    t_reviewer = task_prompts["reviewer_task"]
    reviewer_task = Task(
        description=t_reviewer["description"],
        expected_output=t_reviewer["expected_output"],
        agent=reviewer,
        context=[architect_task, coder_task],
        # output_json is retained to enforce structured output generation.
        # We deliberately rely on CrewAI's fallback mechanism to handle 
        # any potential API incompatibilities with Thinking Mode.
        output_json=ReviewSchema
    )

    # --------------------------------------------------------------------------
    # TASK 4: REMEDIATION (HOTFIX / CONFIRMATION)
    # --------------------------------------------------------------------------
    t_remediation = task_prompts["remediation_task"]
    remediation_task = Task(
        description=t_remediation["description"],
        expected_output=t_remediation["expected_output"],
        agent=engineer,
        # Natively passes the full Reviewer chain-of-thought and structured JSON
        # directly to the Engineer to execute modifications or a No-Op.
        context=[architect_task, coder_task, reviewer_task]
    )
    
    # Assemble the sequential pipeline
    pipeline_crew = Crew(
        agents=[designer, engineer, reviewer],
        tasks=[architect_task, coder_task, reviewer_task, remediation_task],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info("Starting sequential execution: Designer -> Coder -> Reviewer -> Remediation")
    pipeline_crew.kickoff()
    
    logger.info("Multi-agent 4-Step Pipeline executed completely.")
    print("\n" + "="*20 + " DEPLOYMENT MATRIX COMPLETE " + "="*20)
    print("  [SUCCESS] Code compilation committed completely. Please check './output_ansible/' directory.")
    print("=" * 68 + "\n")