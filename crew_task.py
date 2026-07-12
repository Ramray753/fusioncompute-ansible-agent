import os
import sys
import yaml
import logging
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# ==============================================================================
# IMPORT THE NEW PYDANTIC SCHEMA & DYNAMIC AGENT FACTORY
# ==============================================================================
from crew_schema import BlueprintSchema
from crew_agents import create_agents

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

def run_virtualization_orchestrator(user_prompt: str, script_type: int):
    """
    Orchestrates the multi-agent sequential pipeline using synchronized token 
    identifiers, dynamic Agent injection, and isolated tool capabilities.
    """
    logger.info(f"Initializing multi-agent pipeline orchestration for route: {script_type}")
    
    # ==============================================================================
    # DYNAMIC DEPENDENCY INJECTION & FACTORY INITIALIZATION
    # ==============================================================================
    # 1. Instantiate role-based agents configured explicitly for this script_type
    designer, engineer, reviewer = create_agents(script_type)
    
    # 2. Load generic task prompts
    task_prompts = _load_task_prompt_config()
    
    # ==============================================================================
    # TASK 1: ARCHITECTURAL DESIGN & ROUTING PHASE
    # ==============================================================================
    t_architect = task_prompts["architect_task"]
    
    # Inject the user prompt securely directly into the task description
    architect_task_description = t_architect["description"].replace("{user_request}", user_prompt)
    
    architect_task = Task(
        description=architect_task_description,
        expected_output=t_architect["expected_output"],
        agent=designer,
        # Enforce Pydantic validation structure
        output_pydantic=BlueprintSchema
    )
    logger.info("Task 1 [Architectural Design Block] configured with BlueprintSchema.")
    
    # ==============================================================================
    # TASK 2: PRODUCTION CODE COMPILATION PHASE
    # ==============================================================================
    t_coder = task_prompts["coder_task"]
    coder_task = Task(
        description=t_coder["description"],
        expected_output=t_coder["expected_output"],
        agent=engineer,
        context=[architect_task]
    )
    logger.info("Task 2 [Code Compilation Block] securely mapped to context workflow.")
    
    # ==============================================================================
    # TASK 3: AUDIT & QUALITY ASSURANCE REVIEW PHASE
    # ==============================================================================
    t_reviewer = task_prompts["reviewer_task"]
    reviewer_task = Task(
        description=t_reviewer["description"],
        expected_output=t_reviewer["expected_output"],
        agent=reviewer,
        context=[architect_task, coder_task]
    )
    logger.info("Task 3 [Static Quality Gate Block] securely mapped to context workflow.")
    
    # ==============================================================================
    # PIPELINE CRADLE EXECUTION ENGINE
    # ==============================================================================
    production_crew = Crew(
        agents=[designer, engineer, reviewer],
        tasks=[architect_task, coder_task, reviewer_task],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info("Launching waterfall orchestrator kickoff engine loop...")
    production_crew.kickoff()
    
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
        # Prompt the user to select the script routing type (Strictly 1, 2, or 3)
        print("\n[PROMPT] 请选择自动化脚本类型 (Please select the script type for this automation):")
        print("  1. 单资源操作脚本 (Single resource operation script)")
        print("  2. 多资源顺序批量操作脚本 (Multi-resources sequential batch operation script)")
        print("  3. 多资源并行批量操作脚本 (Multi-resources parallel batch operation script)")
        
        script_type_str = input("\nSelect an option (1-3): ").strip()
        
        # Hard validation for routing type selection
        if script_type_str not in ['1', '2', '3']:
            print("[FATAL ERROR] Invalid script type. Must be strictly 1, 2, or 3.")
            sys.exit(1)
            
        # Prompt for the specific automation requirement after the type is defined
        user_input_requirement = input("\n[PROMPT] 请输入您的自动化需求 (Please enter your automation requirement): ").strip()
        
        # Hard validation to ensure the requirement string is never empty
        if not user_input_requirement:
            print("[FATAL ERROR] Requirement validation failed: Input string cannot be empty.")
            sys.exit(1)
            
        # Execute the pipeline with dynamic routing
        run_virtualization_orchestrator(user_input_requirement, int(script_type_str))
        
    except KeyboardInterrupt:
        print("\n[INFO] Orchestration runtime gateway terminated by user. Exiting safely.")