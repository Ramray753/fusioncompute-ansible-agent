from crewai import Crew, Task, Process

# Import our example-driven unified agents from the centralized agents.py script
from agents import virtualization_analyst, python_rest_engineer, ansible_automation_engineer

def run_virtualization_orchestrator(user_prompt: str):
    """
    Orchestrates the entire multi-agent workflow using clean semantic bridging.
    Tasks focus exclusively on dynamic input data and expected output goals,
    completely offloading strict execution guardrails to the Agent's backstory definitions.
    """
    print(f"\n[ORCHESTRATOR] Initializing abstracted infrastructure triage for: '{user_prompt}'")
    
    # ==============================================================================
    # PHASE 1: REQUIREMENTS ANALYSIS & TECHNIQUE ROUTING 
    # ==============================================================================
    analysis_task = Task(
        description=(
            "Thoroughly analyze the incoming request: '{user_request}'.\n"
            "Evaluate whether this implementation requires a raw Python REST API script project "
            "or an Ansible Playbook automation environment.\n"
            "Enforce the specific block token classification constraint as instructed in your profile."
        ),
        expected_output="An absolute architectural routing token followed by sequential atomic breakdown steps.",
        agent=virtualization_analyst
    )
    
    triage_crew = Crew(
        agents=[virtualization_analyst],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=True
    )
    
    analysis_result = triage_crew.kickoff(inputs={"user_request": user_prompt}).raw
    print("\n" + "="*20 + " ARCHITECT ANALYSIS MATRIX GENERATED " + "="*20)
    print(analysis_result)
    print("="*57 + "\n")
    
    routing_lines = analysis_result.strip().splitlines()
    if not routing_lines:
        print("[FATAL] Architect returned an empty blueprint.")
        return
    routing_header = routing_lines[0]
    
    # ==============================================================================
    # PHASE 2A: TRACK 1 RUNTIME - PURE PYTHON REST ENGINE (FULLY DECOUPLED)
    # ==============================================================================
    if "PYTHON_REST" in routing_header:
        print("[ROUTER] Enforcing TRACK: PYTHON_REST. Initializing Python Rest Engineer...")
        
        python_production_task = Task(
            description=(
                f"Implement the following virtualization blueprint: \n{analysis_result}\n\n"
                "CRITICAL DIRECTION:\n"
                "Execute your chronological tool pipeline precisely as defined in your backstory.\n"
                "You are ordered to process the reference code blueprints strictly for parameter comprehension, "
                "while forcing advanced Python modularity and encapsulation as mandated by your profile settings. "
                "Ensure every flashed filename key strictly forces a legal extension suffix."
            ),
            expected_output="A local validation receipt proving that your modular source scripts with explicit .py extensions were flashed.",
            agent=python_rest_engineer
        )
        
        python_crew = Crew(
            agents=[python_rest_engineer],
            tasks=[python_production_task],
            process=Process.sequential,
            verbose=True
        )
        python_crew.kickoff()
        print("\n[DEPLOYMENT] Track 1 execution finalized. Check ./output_python/ directory.")

    # ==============================================================================
    # PHASE 2B: TRACK 2 RUNTIME - DECLARATIVE ANSIBLE PLAYBOOK ENVIRONMENT (FULLY DECOUPLED)
    # ==============================================================================
    elif "ANSIBLE_PLAYBOOK" in routing_header:
        print("[ROUTER] Enforcing TRACK: ANSIBLE_PLAYBOOK. Initializing Streamlined Ansible Orchestrator...")
        
        ansible_production_task = Task(
            description=(
                f"Implement the following virtualization blueprint: \n{analysis_result}\n\n"
                "CRITICAL DIRECTION:\n"
                "Execute your chronological tool lookup sequence precisely as defined in your backstory.\n"
                "You must deliver the finalized file matrix by strictly conforming to all production compliance "
                "mandates, file layout conventions, and anti-pitfall rules established inside your backstory definition. "
                "Do not invent any out-of-scope inventory topologies."
            ),
            expected_output="A topology layout receipt proving that only compliant, numbered, multi-file playbooks with explicit .yml extensions as dictionary keys were flashed.",
            agent=ansible_automation_engineer
        )
        
        ansible_crew = Crew(
            agents=[ansible_automation_engineer],
            tasks=[ansible_production_task],
            process=Process.sequential,
            verbose=True
        )
        ansible_crew.kickoff()
        print("\n[DEPLOYMENT] Track 2 execution successfully finalized. Check ./output_ansible/ directory.")
        
    else:
        print(f"[FATAL ROUTING ERROR] Unrecognized routing token: '{routing_header}'")

# ==============================================================================
# PURE INTERACTIVE COMMAND-LINE GATEWAY ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*21 + " FUSIONCOMPUTE AUTOMATION RUNTIME " + "="*21)
    try:
        # Prompt user directly in the command line session after invoking 'python crew.py'
        # Exmaple: 编写一个Ansible Playbook，指定一个主机名和数据存储名，完成关联该数据存储到主机的操作。
        # Exmaple: 编写一个Ansible Playbook，指定虚拟机名，如果类型为Linux，上传自定义脚本"hostname"，打印执行结果。
        user_input_requirement = input("[PROMPT] Please enter your automation requirement: ").strip()
        if user_input_requirement:
            run_virtualization_orchestrator(user_input_requirement)
        else:
            print("[FATAL ERROR] Requirement validation failed: Input string cannot be empty.")
    except KeyboardInterrupt:
        print("\n[INFO] Orchestration gateway terminated by user. Exiting safely.")