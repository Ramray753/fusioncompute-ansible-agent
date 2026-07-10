import os
import sys
from crewai import Crew, Task, Process

# Import the decoupled architect agent from our centralized agent factory
from agents import ansible_blueprint_designer

def run_architect_test(user_prompt: str):
    """
    Executes an isolated single-task runtime pipeline to evaluate and verify
    the [Automation Architect]'s REST endpoint filtering and topology design logic.
    """
    print(f"\n[TEST_RUN] Initiating isolated architectural design audit for: '{user_prompt}'")
    
    # ==============================================================================
    # ISOLATED TASK: BLUEPRINT GENERATION ONLY
    # ==============================================================================
    isolated_architect_task = Task(
        description=(
            "Thoroughly analyze the incoming infrastructure request: '{user_request}'.\n"
            "Query your directory index maps to identify the exact minimum subset of REST API endpoints "
            "required to fulfill the request. Do NOT include asynchronous task-tracking endpoints. "
            "Deconstruct the target logic into an abstract, multi-file execution workflow design blueprint. "
            "You must explicitly declare task sequences, module selections, and specify REST routes whenever "
            "fc_generic is required. Prepend your final response with the header '### BY: [Automation Architect]'. "
            "Do not generate code."
        ),
        expected_output="A filtered REST API endpoint registry followed by a sequential multi-file execution block topology design blueprint.",
        agent=ansible_blueprint_designer
    )
    
    # Construct a lightweight single-agent crew for fast iterative testing
    test_crew = Crew(
        agents=[ansible_blueprint_designer],
        tasks=[isolated_architect_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Kickoff the agent and capture the final architectural markdown blueprint
    blueprint_result = test_crew.kickoff(inputs={"user_request": user_prompt})
    
    # Stream the resulting blueprint directly to the console for engineer inspection
    print("\n" + "="*20 + " [TEST] ARCHITECT BLUEPRINT OUTPUT " + "="*20)
    print(blueprint_result)
    print("="*68 + "\n")

# ==============================================================================
# INTERACTIVE COMMAND-LINE GATEWAY FOR RAPID TESTING
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*21 + " FUSIONCOMPUTE ARCHITECT VERIFIER " + "="*21)
    try:
        # Prompt the engineer for the specific virtualization orchestration scenario
        user_input_requirement = input("[PROMPT] Enter automation requirement to test design: ").strip()
        if user_input_requirement:
            run_architect_test(user_input_requirement)
        else:
            print("[FATAL ERROR] Input requirement string cannot be empty.")
    except KeyboardInterrupt:
        print("\n[INFO] Test execution runtime terminated by user safely.")