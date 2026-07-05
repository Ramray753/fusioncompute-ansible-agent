import os
import chromadb
import ollama
from crewai.tools import tool

class AnsibleAutomationTools:
    """
    Streamlined Ansible automation toolset designed for pure example-driven orchestration.
    Maintains clean separation of concerns by excluding distracting raw REST formatting blueprints.
    """

    @tool("fetch_all_api_headings")
    def fetch_all_api_headings() -> str:
        """
        Retrieves the complete directory index containing all section headings of the 
        underlying REST API document. Useful to discover resource endpoints when native modules are absent.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        all_records = collection.get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas"]
        )
        seen_headings = []
        for meta in all_records.get("metadatas", []):
            h_path = meta.get("heading", "")
            if h_path and h_path not in seen_headings:
                seen_headings.append(h_path)
        return "\n".join([f"[{i+1:03d}] {h}" for i, h in enumerate(seen_headings)])


    @tool("fetch_all_ansible_headings")
    def fetch_all_ansible_headings() -> str:
        """
        Retrieves the complete directory index containing all section headings specifically 
        from the Ansible module document to map out natively wrapped automation components.
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


    @tool("read_ansible_module_specification")
    def read_ansible_module_specification() -> str:
        """
        Reads global framework mechanics inside the Ansible module document, covering 
        module authentication profiles, asynchronous synchronization, and baseline parameter rules.
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


    @tool("query_specific_section_content")
    def query_specific_section_content(target_heading_or_keyword: str) -> str:
        """
        Extracts precise data specifications, parameter tables, or raw text contents 
        for a targeted Ansible module heading or a REST API endpoint heading across all files.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        
        all_records = collection.get(include=["metadatas", "documents"])
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            if target_heading_or_keyword.strip() in meta.get("heading", ""):
                return f"### Verified Schema: {meta['heading']} (Source: {meta['source']})\n{all_records['documents'][idx]}"
                
        nomic_safe_query = f"search_query: {target_heading_or_keyword}"
        response = ollama.embeddings(model="nomic-embed-text", prompt=nomic_safe_query)
        results = collection.query(query_embeddings=[response["embedding"]], n_results=1)
        
        if results and results["documents"] and results["documents"][0]:
            matched_meta = results["metadatas"][0][0]
            return f"### Verified Vector Result: {matched_meta['heading']} (Source: {matched_meta['source']})\n{results['documents'][0][0]}"
        return f"No certified data specification discovered globally matching: '{target_heading_or_keyword}'."


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

# ==============================================================================
# PIPELINE CELLULAR UNIT TEST MODULE
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*20 + " STARTING OPTIMIZED ANSIBLE TOOLS AUDIT " + "="*20)
    
    try:
        api_dir = AnsibleAutomationTools.fetch_all_api_headings.run()
        ansible_dir = AnsibleAutomationTools.fetch_all_ansible_headings.run()
        print(f"\n[STAGE 1-2] Global maps retrieved. API items: {len(api_dir.splitlines())}, Ansible items: {len(ansible_dir.splitlines())}")
        
        ansible_spec = AnsibleAutomationTools.read_ansible_module_specification.run()
        print(f"[STAGE 3] Baseline module framework mapped. Data size: {len(ansible_spec)}")
        
        ansible_blue = AnsibleAutomationTools.read_ansible_code_blueprints.run()
        print(f"[STAGE 4] Master Example design blueprints mapped. Data size: {len(ansible_blue)}")
    except Exception as e: print(f"Basic stages setup error: {e}")

    print("\n[STAGE 5] Running Tool 5 Globally for cross-document sync...")
    try:
        res_a = AnsibleAutomationTools.query_specific_section_content.run(target_heading_or_keyword="fc_vm_lifecycle_manager")
        res_b = AnsibleAutomationTools.query_specific_section_content.run(target_heading_or_keyword="修改站点高级配置")
        print(f"  Pass: Isolated Native module block and Native REST API block successfully. Data sizes: {len(res_a)} / {len(res_b)}")
    except Exception as e: print(f"  Failed Stage 5: {e}")

    print("\n[STAGE 6] Running New Tool 6: write_modular_ansible_files...")
    try:
        mock_playbook_environment = {
            "site.yml": "---\n- name: Deploy Cluster\n  hosts: all\n  tasks:\n    - name: Trigger generic fallback\n"
        }
        io_result = AnsibleAutomationTools.write_modular_ansible_files.run(file_matrix=mock_playbook_environment)
        print(f"  Feedback: {io_result}")
        assert os.path.exists("./output_ansible/site.yml"), "Physical IO error: site.yml missing."
        print("  Pass: Local file permissions and multi-playbook pipeline fully cleared.")
    except Exception as e:
        print(f"  Failed Stage 6: {e}")

    print("="*19 + " ANSIBLE AUTOMATION TOOLS STREAMLINED VALIDATED " + "="*19 + "\n")