import os
from crewai import Crew, Task, Process

# Import our unified agents from the centralized agents.py script
from agents import virtualization_analyst, python_rest_engineer, ansible_automation_engineer

def run_virtualization_orchestrator(user_prompt: str):
    """
    Orchestrates the entire multi-agent workflow using dynamic condition routing.
    All models are dynamically hot-swapped based on your local .env blueprints.
    """
    print(f"\n[ORCHESTRATOR] Initializing infrastructure triage for: '{user_prompt}'")
    
    # ==============================================================================
    # PHASE 1: REQUIREMENTS ANALYSIS & TECHNIQUE ROUTING 
    # ==============================================================================
    analysis_task = Task(
        description=(
            "Thoroughly analyze the following virtualization provisioning request: '{user_request}'.\n"
            "Determine whether this action requires a raw Python REST API script project "
            "or an Ansible Playbook automation environment.\n"
            "CRITICAL OUTPUT FORMAT CONSTRAINT:\n"
            "The very first line of your response MUST be exactly one of the following tokens:\n"
            "  'TRACK: PYTHON_REST'\n"
            "  'TRACK: ANSIBLE_PLAYBOOK'\n"
            "Immediately after this token, provide an atomic, step-by-step technical "
            "breakdown of the virtualization deployment phases."
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
    
    # Execute triage stage and extract the raw string insight
    analysis_result = triage_crew.kickoff(inputs={"user_request": user_prompt}).raw
    print("\n" + "="*20 + " ARCHITECT ANALYSIS MATRIX GENERATED " + "="*20)
    print(analysis_result)
    print("="*57 + "\n")
    
    # Parse the routing header token from the first line
    routing_lines = analysis_result.strip().splitlines()
    if not routing_lines:
        print("[FATAL] Architect returned an empty blueprint.")
        return
    routing_header = routing_lines[0]
    
    # ==============================================================================
    # PHASE 2A: TRACK 1 RUNTIME - PURE PYTHON REST ENGINE 
    # ==============================================================================
    if "PYTHON_REST" in routing_header:
        print("[ROUTER] Enforcing TRACK: PYTHON_REST. Initializing Python Rest Engineer...")
        
        python_production_task = Task(
            description=(
                f"Implement the following virtualization blueprint: \n{analysis_result}\n\n"
                "You must construct a complete, production-grade modular Python script architecture.\n"
                "STRICT 5-STAGE LOOKUP WORKFLOW:\n"
                "  1. Run tool 'fetch_all_api_headings' to map global API headings.\n"
                "  2. Run tool 'read_api_format_specification' to digest raw protocol rules under 'API接口格式'.\n"
                "  3. Run tool 'read_api_code_blueprints' to analyze native cURL blueprints and exact JSON nesting responses.\n"
                "  4. Run tool 'query_specific_section_content' repeatedly to gather parameter tables for target actions.\n"
                "  5. Autonomously design a modular project structure and invoke tool 'write_modular_python_files' to flash files.\n"
                "FINAL REQUISITE: You MUST pass your finalized multi-file code matrix into "
                "tool 'write_modular_python_files' to execute dynamic deployment onto the disk.\n"
                "All code comments inside your generated python files MUST be written in English."
            ),
            expected_output="A local validation receipt proving that your modular source scripts were cleanly flashed.",
            agent=python_rest_engineer
        )
        
        python_crew = Crew(
            agents=[python_rest_engineer],
            tasks=[python_production_task],
            process=Process.sequential,
            verbose=True
        )
        python_crew.kickoff()
        print("\n[DEPLOYMENT] Track 1 execution successfully finalized. Check ./output_python/ directory.")

    # ==============================================================================
    # PHASE 2B: TRACK 2 RUNTIME - DECLARATIVE ANSIBLE PLAYBOOK ENVIRONMENT
    # ==============================================================================
    elif "ANSIBLE_PLAYBOOK" in routing_header:
        print("[ROUTER] Enforcing TRACK: ANSIBLE_PLAYBOOK. Initializing Ansible Orchestrator...")
        
        ansible_production_task = Task(
            description=(
                f"Implement the following virtualization blueprint: \n{analysis_result}\n\n"
                "You must construct an error-immune, declarative Ansible environment.\n"
                "STRICT 8-STAGE LOOKUP WORKFLOW:\n"
                "  1. Execute tool 'fetch_all_api_headings' and 'fetch_all_ansible_headings' to map global dual directories.\n"
                "  2. Execute tool 'read_api_format_specification' and 'read_ansible_module_specification' to digest specifications.\n"
                "  3. Execute tool 'read_api_code_blueprints' and 'read_ansible_code_blueprints' to analyze formatting blueprints.\n"
                "  4. Execute tool 'query_specific_section_content' repeatedly to pull parameters for specific structures.\n"
                "  5. Autonomously decouple your environment topology into separate files via tool 'write_modular_ansible_files'.\n"
                "CRITICAL BUSINESS FALLBACK SKILL: If dedicated native modules are missing or parameter-constrained, "
                "instantly activate your 'fc_generic 终极兜底' strategy by pulling raw REST structures via 'query_specific_section_content'.\n"
                "FINAL REQUISITE: You MUST invoke tool 'write_modular_ansible_files' to flush the environment.\n"
                "All code comments inside your generated automation files MUST be written in English."
            ),
            expected_output="A topology layout receipt proving that all playbooks and inventories were cleanly flashed.",
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
        print(f"[FATAL ROUTING ERROR] Unrecognized routing token generated by architect: '{routing_header}'")

if __name__ == "__main__":
    production_test_prompt = "编写一个Ansible Playbook，指定一个主机名和数据存储名，在FusionCompute上完成关联该数据存储到主机的操作。"
    run_virtualization_orchestrator(production_test_prompt)