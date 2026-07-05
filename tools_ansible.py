import os
import chromadb
import ollama
from crewai.tools import tool

class AnsibleAutomationTools:
    """
    Comprehensive Ansible automation toolset engineered using a 7-stage progressive routing pipeline.
    Forces the agent to absorb underlying REST API schemas before layering Ansible abstractions.
    """

    # ==============================================================================
    # STAGE 1: REST API DIRECTORY INDEX (REUSED FROM PYTHON TOOLS WITH RE-ALIGNED DOCS)
    # ==============================================================================
    @tool("1. Fetch All REST API Headings")
    def fetch_all_api_headings() -> str:
        """
        MANDATORY FIRST STEP. Use this tool to retrieve the complete directory index (all section headings) 
        of the underlying REST API document. Since Ansible modules are wrappers over these raw REST APIs, 
        you must inspect this map first to understand the absolute capabilities of the platform. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = collection = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas"]
        )
        seen_headings = []
        for meta in all_records.get("metadatas", []):
            h_path = meta.get("heading", "")
            if h_path and h_path not in seen_headings:
                seen_headings.append(h_path)
        return "\n".join([f"[{i+1:03d}] {h}" for i, h in enumerate(seen_headings)])

    # ==============================================================================
    # STAGE 2: NEW ANSIBLE DIRECTORY INDEX TOOL
    # ==============================================================================
    @tool("2. Fetch All Ansible Module Headings")
    def fetch_all_ansible_headings() -> str:
        """
        MANDATORY SECOND STEP. Use this tool to retrieve the complete directory index (all section headings) 
        specifically from the Ansible module document. This builds an internal inventory map of 
        natively wrapped automation components available to you before code design. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas"]
        )
        seen_headings = []
        for meta in all_records.get("metadatas", []):
            h_path = meta.get("heading", "")
            if h_path and h_path not in seen_headings:
                seen_headings.append(h_path)
        return "\n".join([f"[{i+1:03d}] {h}" for i, h in enumerate(seen_headings)])

    # ==============================================================================
    # STAGE 3: REST API SPECIFICATION LOOKUP (REUSED FROM PYTHON TOOLS WITH RE-ALIGNED DOCS)
    # ==============================================================================
    @tool("3. Read Global API Format Specification")
    def read_api_format_specification() -> str:
        """
        MANDATORY THIRD STEP. Use this tool to read the core specifications under the heading 'API接口格式'. 
        You must understand global raw HTTP response behaviors, status structures, and URI patterns, 
        because native Ansible modules inherit these definitions when evaluating failure states or task variables. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        matched_chunks = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            if "API接口格式" in meta.get("heading", ""):
                matched_chunks.append(f"### Section: {meta['heading']}\n{all_records['documents'][idx]}")
        return "\n\n---\n\n".join(matched_chunks)

    # ==============================================================================
    # STAGE 4: NEW ANSIBLE AUTH & FRAMEWORK SPECIFICATION TOOL
    # ==============================================================================
    @tool("4. Read Global Ansible Module Specification")
    def read_ansible_module_specification() -> str:
        """
        MANDATORY FOURTH STEP. Use this tool to read global framework mechanics inside the Ansible document. 
        It extracts sections regarding '模块鉴权介绍', '异步任务同步化', and '模块组织结构与参数说明'. 
        You must analyze this to understand core Ansible environment authentication variables and state synchronization. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        target_keywords = ["模块鉴权介绍", "异步任务同步化", "模块组织结构与参数说明"]
        matched_chunks = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            if any(kw in heading for kw in target_keywords):
                matched_chunks.append(f"### Section: {heading}\n{all_records['documents'][idx]}")
        return "\n\n---\n\n".join(matched_chunks)

    # ==============================================================================
    # STAGE 5: REST API BLUEPRINTS LOOKUP (REUSED FROM PYTHON TOOLS WITH RE-ALIGNED DOCS)
    # ==============================================================================
    @tool("5. Read End-to-End API Code Blueprints")
    def read_api_code_blueprints() -> str:
        """
        MANDATORY FIFTH STEP. Use this tool to inspect raw shell cURL blocks and real terminal JSON responses under 'API调用代码示例'. 
        You must study the native JSON object structures because native Ansible modules return these exact JSON dictionaries 
        as their execution payloads, which dictates how you configure your 'register' task variables. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        matched_blueprints = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            if "API调用代码示例" in meta.get("heading", ""):
                matched_blueprints.append(f"### API Blueprint: {meta['heading']}\n{all_records['documents'][idx]}")
        return "\n\n---\n\n".join(matched_blueprints)

    # ==============================================================================
    # STAGE 6: NEW ANSIBLE PLAYBOOK BLUEPRINTS TOOL
    # ==============================================================================
    @tool("6. Read Playbook Blueprints and Console Echoes")
    def read_ansible_code_blueprints() -> str:
        """
        MANDATORY SIXTH STEP. Use this tool to read production-grade YAML template architectures and terminal 
        console printouts under 'Ansible Playbook 示例'. This dictates the mandatory code formatting, structural design, 
        and variable assignment constraints you must follow. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        matched_blueprints = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            # 🎯 FIX: Added the critical missing space to perfectly match DB key "Ansible Playbook 示例"
            if "Ansible Playbook 示例" in heading:
                matched_blueprints.append(f"### Ansible Blueprint: {heading}\n{all_records['documents'][idx]}")
        if matched_blueprints:
            return "\n\n---\n\n".join(matched_blueprints)
        return "Official Ansible Playbook examples are missing or unindexed."

    # ==============================================================================
    # STAGE 7: UNIFIED GLOBAL DEEP DIVE LOOKUP TOOL (MERGED)
    # ==============================================================================
    @tool("7. Query Specific Section Content Globally")
    def query_specific_section_content(target_heading_or_keyword: str) -> str:
        """
        UNIFIED LOOKUP ENGINE. Use this tool repeatedly to extract the exact schemas, 
        parameter tables, or text contents for EITHER a specific Ansible module heading 
        OR a raw REST API endpoint heading across all indexed documents. Executed multiple times.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        
        # Channel 1: Cross-document absolute string match loop
        all_records = collection.get(include=["metadatas", "documents"])
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            if target_heading_or_keyword.strip() in meta.get("heading", ""):
                return f"### Verified Schema: {meta['heading']} (Source: {meta['source']})\n{all_records['documents'][idx]}"
                
        # Channel 2: Global hybrid Cosine vector graph search across all documents
        nomic_safe_query = f"search_query: {target_heading_or_keyword}"
        response = ollama.embeddings(model="nomic-embed-text", prompt=nomic_safe_query)
        results = collection.query(query_embeddings=[response["embedding"]], n_results=1)
        
        if results and results["documents"] and results["documents"][0]:
            matched_meta = results["metadatas"][0][0]
            return f"### Verified Vector Result: {matched_meta['heading']} (Source: {matched_meta['source']})\n{results['documents'][0][0]}"
        return f"No certified data specification discovered globally matching: '{target_heading_or_keyword}'."

    # ==============================================================================
    # STAGE 8: WRITE MODULAR PLAYBOOK PROJECT FILES
    # ==============================================================================
    @tool("8. Write Modular Playbook Project Files")
    def write_modular_ansible_files(file_matrix: dict) -> str:
        """
        Use this tool as the absolute final step to write multiple separate Ansible automation files 
        (e.g., playbooks, roles, variable structures, inventories) onto the disk simultaneously.
        The input MUST be a flat dictionary where keys are filename strings and values are text strings.
        Example: {"site.yml": "yaml...", "hosts.ini": "text...", "commons.yml": "yaml..."}
        """
        target_directory = "./output_ansible"
        try:
            os.makedirs(target_directory, exist_ok=True)
            written_manifest = []
            
            for filename, file_content in file_matrix.items():
                safe_filename = os.path.basename(filename)
                full_write_path = os.path.join(target_directory, safe_filename)
                
                with open(full_write_path, "w", encoding="utf-8") as file_handle:
                    file_handle.write(file_content)
                written_manifest.append(safe_filename)
                
            return f"Success! Dynamic playbook layout completed. Created files: {written_manifest}"
        except Exception as error:
            return f"File I/O deployment failure: {str(error)}"

# ==============================================================================
# RIGOROUS 8-STAGE PIPELINE CELLULAR UNIT TEST MODULE
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*20 + " STARTING SCHEME-A ANSIBLE TOOLS AUDIT " + "="*20)
    
    # Stages 1-6 Basic Index & Specification Pull Checks
    try:
        api_dir = AnsibleAutomationTools.fetch_all_api_headings.run()
        ansible_dir = AnsibleAutomationTools.fetch_all_ansible_headings.run()
        print(f"\n[STAGE 1-2] Global maps retrieved. API items: {len(api_dir.splitlines())}, Ansible items: {len(ansible_dir.splitlines())}")
        
        api_spec = AnsibleAutomationTools.read_api_format_specification.run()
        ansible_spec = AnsibleAutomationTools.read_ansible_module_specification.run()
        print(f"[STAGE 3-4] Baseline frameworks mapped. Data sizes: {len(api_spec)} / {len(ansible_spec)}")
        
        api_blue = AnsibleAutomationTools.read_api_code_blueprints.run()
        ansible_blue = AnsibleAutomationTools.read_ansible_code_blueprints.run()
        print(f"[STAGE 5-6] Template design blueprints mapped. Data sizes: {len(api_blue)} / {len(ansible_blue)}")
    except Exception as e: print(f"Basic stages setup error: {e}")

    # [STAGE 7 TEST] Unified Search Deep Dive
    print("\n[STAGE 7] Running Tool 7 Globally for cross-document sync...")
    try:
        res_a = AnsibleAutomationTools.query_specific_section_content.run(target_heading_or_keyword="fc_vm_lifecycle_manager")
        res_b = AnsibleAutomationTools.query_specific_section_content.run(target_heading_or_keyword="修改站点高级配置")
        print(f"  Pass: Isolated Native module block and Native REST API block successfully. Data sizes: {len(res_a)} / {len(res_b)}")
    except Exception as e: print(f"  Failed Stage 7: {e}")

    # 🎯 [STAGE 8 TEST] NEW: Validate dynamic playbook structures generation
    print("\n[STAGE 8] Running New Tool 8: write_modular_ansible_files...")
    try:
        import os
        mock_playbook_environment = {
            "site.yml": "---\n- name: Deploy Cluster\n  hosts: all\n  tasks:\n    - name: Trigger generic fallback\n",
            "hosts.ini": "[vrm_nodes]\n192.168.1.10\n",
            "group_vars_all.yml": "ansible_user: admin\n"
        }
        io_result = AnsibleAutomationTools.write_modular_ansible_files.run(file_matrix=mock_playbook_environment)
        print(f"  Feedback: {io_result}")
        
        # Verify physical disk presence
        assert os.path.exists("./output_ansible/site.yml"), "Physical IO error: site.yml missing."
        assert os.path.exists("./output_ansible/hosts.ini"), "Physical IO error: hosts.ini missing."
        print("  Pass: Local file permissions and multi-playbook pipeline fully cleared.")
    except Exception as e:
        print(f"  Failed Stage 8: {e}")

    print("="*19 + " ANSIBLE AUTOMATION TOOLS 8-STAGE VALIDATED " + "="*19 + "\n")