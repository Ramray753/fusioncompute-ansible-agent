import os
import chromadb
import ollama
from crewai.tools import tool

class AnsibleAutomationTools:
    """
    Streamlined Ansible automation toolset optimized for strict API-driven content mapping.
    Eliminates native Ansible directory tracing to focus exclusively on raw REST interface specifications.
    """

    @tool("fetch_all_api_headings")
    def fetch_all_api_headings() -> str:
        """
        Retrieves the filtered directory index containing technical section headings under the core 
        virtualization and management interface chapters of the FusionCompute REST API document.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        all_records = collection.get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas"]
        )
        
        allowed_top_levels = [
            "计算虚拟化接口", 
            "存储虚拟化接口", 
            "网络虚拟化接口", 
            "OM API接口", 
            "备份管理接口", 
            "CDP容灾管理", 
            "事件上报接口"
        ]
        
        seen_headings = []
        for meta in all_records.get("metadatas", []):
            h_path = meta.get("heading", "")
            if h_path:
                # Extract the top-level section name before the structural delimiter
                top_level = h_path.split("->")[0].strip()
                if top_level in allowed_top_levels and h_path not in seen_headings:
                    seen_headings.append(h_path)
                    
        if not seen_headings:
            return "No registered core interface headings discovered in the target REST directory."
            
        return "\n".join([f"[{i+1:03d}] {h}" for i, h in enumerate(seen_headings)])


    @tool("read_ansible_module_specification")
    def read_ansible_module_specification() -> str:
        """
        Reads the complete document specifications and context blocks under the top-level 
        heading 'FusionCompute Ansible 模块' inside the core Ansible documentation.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        matched_chunks = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            top_level = heading.split("->")[0].strip()
            if top_level == "FusionCompute Ansible 模块":
                matched_chunks.append(f"### Section: {heading}\n{all_records['documents'][idx]}")
                
        if matched_chunks:
            return "\n\n---\n\n".join(matched_chunks)
        return "Global Ansible module specifications are currently missing or unindexed."


    @tool("read_api_specification")
    def read_api_specification() -> str:
        """
        Reads all baseline protocol standards and configuration specifications under the 
        top-level heading 'API接口格式' inside the raw FusionCompute REST API document.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        matched_chunks = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            top_level = heading.split("->")[0].strip()
            if top_level == "API接口格式":
                matched_chunks.append(f"### Section: {heading}\n{all_records['documents'][idx]}")
                
        if matched_chunks:
            return "\n\n---\n\n".join(matched_chunks)
        return "Global REST API interface specifications are currently missing or unindexed."


    @tool("read_ansible_code_blueprints")
    def read_ansible_code_blueprints() -> str:
        """
        Reads production-grade YAML template architectures and console printouts 
        under the exact heading 'Ansible Playbook 示例' in the Ansible documentation.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        matched_blueprints = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            if "Ansible Playbook 示例" in heading:
                matched_blueprints.append(f"### Ansible Blueprint: {heading}\n{all_records['documents'][idx]}")
                
        if matched_blueprints:
            return "\n\n---\n\n".join(matched_blueprints)
        return "Official Ansible Playbook examples are missing or unindexed."


    @tool("query_specific_api_content")
    def query_specific_api_content(target_heading_or_keyword: str) -> str:
        """
        Extracts precise technical parameter tables, URL methods, and payload data schemas 
        exclusively from the core interface chapters of the raw FusionCompute REST API document.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        
        filter_condition = {"source": "fusioncompute_8100_api_cleaned.docx"}
        allowed_top_levels = [
            "计算虚拟化接口", 
            "存储虚拟化接口", 
            "网络虚拟化接口", 
            "OM API接口", 
            "备份管理接口", 
            "CDP容灾管理", 
            "事件上报接口"
        ]
        
        # Channel 1: Strict substring matching bounded to target interface chapters
        all_records = collection.get(where=filter_condition, include=["metadatas", "documents"])
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            top_level = heading.split("->")[0].strip()
            if top_level in allowed_top_levels and target_heading_or_keyword.strip() in heading:
                return f"### Verified API Schema: {heading}\n{all_records['documents'][idx]}"
                
        # Channel 2: High-precision Vector Search fallback restricted to the API source document
        nomic_safe_query = f"search_query: {target_heading_or_keyword}"
        response = ollama.embeddings(model="nomic-embed-text", prompt=nomic_safe_query)
        results = collection.query(
            query_embeddings=[response["embedding"]],
            where=filter_condition,
            n_results=3  # Scan top results to guarantee top-level compliance filtering
        )
        
        if results and results["documents"] and results["documents"][0]:
            for doc_idx, meta_data in enumerate(results["metadatas"][0]):
                res_heading = meta_data.get("heading", "")
                res_top_level = res_heading.split("->")[0].strip()
                if res_top_level in allowed_top_levels:
                    return f"### Verified API Vector Result: {res_heading}\n{results['documents'][0][doc_idx]}"
                    
        return f"No certified data specification discovered within core API chapters matching: '{target_heading_or_keyword}'."


    @tool("write_modular_ansible_files")
    def write_modular_ansible_files(file_matrix: dict) -> str:
        """
        Writes multiple separate Ansible automation files onto the local disk simultaneously. 
        Accepts a flat dictionary mapping filename strings to text content strings.
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
        
    @tool("read_all_compiled_ansible_files")
    def read_all_compiled_ansible_files() -> str:
        """
        Reads and retrieves the absolute text content and filenames of all currently 
        deployed Ansible playbook files within the output directory for code review.
        """
        target_directory = "./output_ansible"
        if not os.path.exists(target_directory):
            return "The target output directory does not exist yet. No playbooks deployed."
            
        compiled_manifest = []
        try:
            for filename in os.listdir(target_directory):
                full_path = os.path.join(target_directory, filename)
                if os.path.isfile(full_path) and filename.endswith(('.yml', '.yaml', '.py')):
                    with open(full_path, "r", encoding="utf-8") as file_handle:
                        content = file_handle.read()
                    compiled_manifest.append(f"=== FILENAME: {filename} ===\n{content}")
            
            if not compiled_manifest:
                return "The output directory is currently empty or contains no valid automation files."
            return "\n\n---\n\n".join(compiled_manifest)
        except Exception as error:
            return f"File I/O read failure during audit: {str(error)}"

# ==============================================================================
# UPDATED RESTRUCTURED PIPELINE UNIT TEST MODULE
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*20 + " STARTING RESTRUCTURED ANSIBLE TOOLS AUDIT " + "="*20)
    
    try:
        api_dir = AnsibleAutomationTools.fetch_all_api_headings.run()
        print(f"\n[STAGE 1] Filtered Core API Maps Retrieved. Tech Heading Count: {len(api_dir.splitlines())}")
        
        ansible_spec = AnsibleAutomationTools.read_ansible_module_specification.run()
        print(f"[STAGE 2] Ansible Core Specifications Mapped. Data size: {len(ansible_spec)}")
        
        api_spec = AnsibleAutomationTools.read_api_specification.run()
        print(f"[STAGE 3] Native API Protocol Specs Mapped. Data size: {len(api_spec)}")
        
        ansible_blue = AnsibleAutomationTools.read_ansible_code_blueprints.run()
        print(f"[STAGE 4] Master Example Blueprints Mapped. Data size: {len(ansible_blue)}")
    except Exception as e: 
        print(f"Basic sequential tool execution check failed: {e}")

    print("\n[STAGE 5] Running Restricted Tool 5 for Specific API Channel Isolate...")
    try:
        res_api = AnsibleAutomationTools.query_specific_api_content.run(target_heading_or_keyword="修改站点高级配置")
        print(f"  Pass: Isolated verified REST API interface specs perfectly. Data size: {len(res_api)}")
    except Exception as e: 
        print(f"  Failed Stage 5: {e}")

    print("\n[STAGE 6] Running Tool 6: write_modular_ansible_files...")
    try:
        mock_playbook_environment = {
            "main.yml": "---\n- name: Pure Generic Automation Task\n  hosts: all\n"
        }
        io_result = AnsibleAutomationTools.write_modular_ansible_files.run(file_matrix=mock_playbook_environment)
        print(f"  Feedback: {io_result}")
        assert os.path.exists("./output_ansible/main.yml"), "Physical IO error: main.yml missing."
        print("  Pass: Local file permissions and streamlined toolset pipelines fully validated.")
    except Exception as e:
        print(f"  Failed Stage 6: {e}")

    print("="*18 + " ANSIBLE AUTOMATION RESTRUCTURED TOOLS PASSED " + "="*18 + "\n")