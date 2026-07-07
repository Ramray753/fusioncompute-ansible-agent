import os
import yaml
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# Import our decoupled multi-agent factory from the centralized agents.py script
from agents import ansible_blueprint_designer, ansible_code_engineer, ansible_code_reviewer

def _load_task_prompt_config() -> dict:
    """
    Helper function to load multi-line structural task descriptions and expectations
    from the external decoupled config matrix 'tasks.yaml'.
    """
    config_file = "tasks.yaml"
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"[FATAL ERROR] Requisite task asset file '{config_file}' is missing from workspace.")
    
    with open(config_file, "r", encoding="utf-8") as file_handle:
        try:
            return yaml.safe_load(file_handle)
        except Exception as error:
            raise ValueError(f"[PARSING ERROR] Failed to load structural task yaml from {config_file}. Details: {str(error)}")

def run_virtualization_orchestrator(user_prompt: str):
    """
    Orchestrates the multi-agent sequential pipeline using synchronized token 
    identifiers and explicit file-system context handshakes.
    """
    print(f"\n[ORCHESTRATOR] Initializing multi-agent pipeline orchestration for: '{user_prompt}'")
    
    # Load fully decoupled task blueprints from external config storage matrix
    task_prompts = _load_task_prompt_config()
    
    # ==============================================================================
    # TASK 1: ARCHITECTURAL DESIGN & ROUTING PHASE
    # ==============================================================================
    t_architect = task_prompts["architect_task"]
    architect_task = Task(
        description=t_architect["description"],
        expected_output=t_architect["expected_output"],
        agent=ansible_blueprint_designer
    )
    
    # ==============================================================================
    # TASK 2: PRODUCTION CODE COMPILATION PHASE (CONTEXT BOUND TO TASK 1)
    # ==============================================================================
    t_coder = task_prompts["coder_task"]
    coder_task = Task(
        description=t_coder["description"],
        expected_output=t_coder["expected_output"],
        agent=ansible_code_engineer,
        context=[architect_task] # Handshake: Restricts coder to the architect's boundaries
    )
    
    # ==============================================================================
    # TASK 3: AUDIT & QUALITY ASSURANCE REVIEW PHASE (CONTEXT BOUND TO TASKS 1 & 2)
    # ==============================================================================
    t_reviewer = task_prompts["reviewer_task"]
    reviewer_task = Task(
        description=t_reviewer["description"],
        expected_output=t_reviewer["expected_output"],
        agent=ansible_code_reviewer,
        context=[architect_task, coder_task] # Handshake: Grants full visibility into designs and code
    )
    
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
        process=Process.sequential, # Enforce strict waterfall progression
        verbose=True
    )
    
    production_crew.kickoff(inputs={"user_request": user_prompt})
    print("\n[DEPLOYMENT] Pipeline orchestration executed completely. Check ./output_ansible/ directory.")

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
        print("\n[INFO] Orchestration gateway terminated by user. Exiting safely.")