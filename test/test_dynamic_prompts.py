import os
import sys
from dotenv import load_dotenv

# ==============================================================================
# WORKSPACE PATH RESOLUTION & SYS.PATH INJECTION
# ==============================================================================
# Resolve the absolute path of the root directory (one level up from 'test/')
# This ensures Python can find root-level modules like crew_agents.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Bootstrap environment variables
load_dotenv()

# Import the dynamic agent factory
from crew_agents import create_agents


def display_agent_info(agent_title: str, agent):
    """
    Helper function to cleanly format and print the dynamically rendered
    agent properties (role, goal, backstory) and their attached tools.
    """
    print(f"\n{'='*20} {agent_title.upper()} {'='*20}")
    print(f"[ROLE] {agent.role}")
    print(f"[GOAL] {agent.goal}")
    print("-" * 80)
    print("[BACKSTORY / DYNAMIC PROMPT]")
    print(agent.backstory.strip())
    print("-" * 80)
    print("[AVAILABLE TOOLS]")
    if agent.tools:
        for tool in agent.tools:
            # Replace newlines with spaces for a cleaner console layout
            clean_desc = tool.description.strip().replace('\n', ' ')
            print(f"  -> {tool.name}: {clean_desc}")
    else:
        print("  -> None assigned")
    print("=" * 80)

def run_routing_inspection(user_prompt: str):
    """
    Simulates the pipeline initialization by generating and inspecting agents 
    across all three routing modes.
    """
    print(f"\n{'#'*30} DYNAMIC ROUTING INSPECTOR {'#'*30}")
    print(f"Simulating pipeline for User Request: '{user_prompt}'\n")

    routing_modes = {
        1: "Single Resource Script (No Batch Operations)",
        2: "Sequential Batch Script",
        3: "Parallel Batch Script"
    }

    for script_type, mode_name in routing_modes.items():
        print(f"\n\n\n{'*'*85}")
        print(f"*** ROUTING MODE {script_type}: {mode_name.upper()}")
        print(f"{'*'*85}")
        
        try:
            # Call the factory to generate agents based on the current script_type
            designer, engineer, reviewer = create_agents(script_type)
            
            # Print the dynamically rendered configuration for each agent
            display_agent_info("Automation Architect", designer)
            display_agent_info("Code Engineer", engineer)
            display_agent_info("Code Reviewer", reviewer)
            
        except Exception as e:
            print(f"[FATAL ERROR] Failed to instantiate agents for mode {script_type}. Details: {str(e)}")

if __name__ == "__main__":
    # Execute the test with the required dummy string
    run_routing_inspection("TEST")