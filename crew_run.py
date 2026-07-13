import sys
# Import the main orchestration function
from crew_task import run_virtualization_orchestrator

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