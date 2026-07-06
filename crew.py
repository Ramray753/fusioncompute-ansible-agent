from crewai import Crew, Task, Process

# Import our decoupled multi-agent factory from the centralized agents.py script
from agents import ansible_blueprint_designer, ansible_code_engineer, ansible_code_reviewer

def run_virtualization_orchestrator(user_prompt: str):
    """
    Orchestrates the multi-agent sequential pipeline using synchronized token 
    identifiers and explicit file-system context handshakes.
    """
    print(f"\n[ORCHESTRATOR] Initializing multi-agent pipeline orchestration for: '{user_prompt}'")
    
    # ==============================================================================
    # TASK 1: ARCHITECTURAL DESIGN & ROUTING PHASE
    # ==============================================================================
    architect_task = Task(
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
    
    # ==============================================================================
    # TASK 2: PRODUCTION CODE COMPILATION PHASE (CONTEXT BOUND TO TASK 1)
    # ==============================================================================
    coder_task = Task(
        description=(
            "Analyze the technical endpoint registry and execution workflow design provided by the upstream [Automation Architect].\n"
            "Query the detailed parameter schemas for the specified endpoints. Translate the abstract layout "
            "into an operating, production-grade multi-file Ansible playbook environment using exclusively the "
            "generic module framework for platform transactions. Commit the file matrix containing 'main.yml', "
            "'commons.yml', and 'wait_fc_system_task.yml' to disk by strictly enforcing your 6 high-density compliance rules."
        ),
        expected_output="A deployment log or matrix confirmation showing that the initial yml file structure was flashed to disk.",
        agent=ansible_code_engineer,
        context=[architect_task] # Handshake: Restricts coder to the architect's specific technical boundaries
    )
    
    # ==============================================================================
    # TASK 3: AUDIT & QUALITY ASSURANCE REVIEW PHASE (CONTEXT BOUND TO TASKS 1 & 2)
    # ==============================================================================
    reviewer_task = Task(
        description=(
            "Perform a rigorous compliance audit on the deployed Ansible playbook code matrix.\n"
            "First, execute your local read tool to fetch the actual text content of the playbooks written by the [Code Engineer] from disk. "
            "Simultaneously cross-reference the retrieved code against the [Automation Architect]'s structural workflow design "
            "and the 6 high-density production compliance rules established inside your backstory profile. "
            "Pay absolute attention to response path formatting patterns and fc_generic syntax. "
            "If any structural defects, key-suffix mutations, or payload discrepancies are discovered, "
            "execute your write tool to save the remediated, compliant code back to disk."
        ),
        expected_output="A final layout receipt validating compliance across all 6 high-density constraints, with explicit file keys committed to disk.",
        agent=ansible_code_reviewer,
        context=[architect_task] # Handshake: Grants full visibility into both blueprints and source code
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
        # Prompt user directly in the command line session after invoking 'python crew.py'
        # Exmaple 1: 编写一个Ansible Playbook，用户指定一个虚拟机名称，如果其本身状态为开机，则执行关机操作；如果其本身状态为关机，则执行开机操作。
        # Exmaple 2: 编写一个Ansible Playbook，用户指定一个虚拟机名称，查询到ID和操作系统类型。如果这个虚拟机类型为Linux，通过API接口"给虚拟机上传自定义脚本"上传自定义脚本，脚本内容为"hostname"；如果这个虚拟机类型为Windows，通过API接口"给虚拟机上传自定义脚本"上传自定义脚本，脚本内容为"Get-ComputerInfo"。等待任务执行结束后，打印执行结果。
        # Exmaple 3: 编写一个Ansible Playbook，用户指定一个CSV文件路径（./vm_names.csv），通过虚拟机详细信息查询Tools的运行状态和版本，并将结果汇总到./vm_tools.csv，文件包含4列（虚拟机名，ID，Tools状态，Tools版本），如果虚拟机名称对应多个ID则仅考虑第一个。每个虚拟机并发查询，并发度为10，并发度定义在commons.yml文件中。
        # Exmaple 4: 编写一个Ansible Playbook，用户指定两个CSV文件路径（./host_names.csv和./datastore_names.csv），这两个CSV文件没有表头，host_names.csv代表主机名称列表，datastore_names.csv表示数据存储名称列表。对于每个主机和数据存储，完成主机关联数据存储操作，串行执行。
        user_input_requirement = input("[PROMPT] Please enter your automation requirement: ").strip()
        if user_input_requirement:
            run_virtualization_orchestrator(user_input_requirement)
        else:
            print("[FATAL ERROR] Requirement validation failed: Input string cannot be empty.")
    except KeyboardInterrupt:
        print("\n[INFO] Orchestration gateway terminated by user. Exiting safely.")