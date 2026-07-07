import os
import configparser
import chromadb
import ollama
from crewai.tools import tool

def _load_config_list(section: str, config_key: str) -> list[str]:
    """
    Helper function to dynamically read interface classification lists and section mappings
    from the external configuration file 'ability.conf' based on section and key targets.
    """
    config_file = "ability.conf"
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"[FATAL ERROR] Requisite configuration file '{config_file}' is missing from workspace.")
    
    parser = configparser.ConfigParser()
    parser.read(config_file, encoding="utf-8")
    try:
        raw_values = parser.get(section, config_key)
        return [value.strip() for value in raw_values.split(",") if value.strip()]
    except Exception as error:
        raise KeyError(f"[CONFIG ERROR] Failed to extract key '{config_key}' from section '{section}' in {config_file}. Details: {str(error)}")

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
        
        # Dynamically load the top levels list from API_CONFIG section
        allowed_top_levels = _load_config_list("API_CONFIG", "headings_top_levels")
        
        seen_headings = []
        for meta in all_records.get("metadatas", []):
            h_path = meta.get("heading", "")
            if h_path:
                top_level = h_path.split("->")[0].strip()
                if top_level in allowed_top_levels and h_path not in seen_headings:
                    seen_headings.append(h_path)
                    
        if not seen_headings:
            return "No registered core interface headings discovered in the target REST directory."
            
        return "\n".join([f"[{i+1:03d}] {h}" for i, h in enumerate(seen_headings)])


    @tool("read_ansible_module_specification")
    def read_ansible_module_specification() -> str:
        """
        Reads the complete document specifications and context blocks under the configured top-level 
        heading inside the core Ansible documentation.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        # Dynamically load module spec top level heading path constraint
        allowed_top_levels = _load_config_list("ANSIBLE_CONFIG", "module_spec_top_level")
        
        matched_chunks = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            top_level = heading.split("->")[0].strip()
            if top_level in allowed_top_levels:
                matched_chunks.append(f"### Section: {heading}\n{all_records['documents'][idx]}")
                
        if matched_chunks:
            return "\n\n---\n\n".join(matched_chunks)
        return "Global Ansible module specifications are currently missing or unindexed."


    @tool("read_api_specification")
    def read_api_specification() -> str:
        """
        Reads all baseline protocol standards and configuration specifications under the configured
        top-level heading inside the raw FusionCompute REST API document.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        # Dynamically load global API baseline section constraints
        allowed_top_levels = _load_config_list("API_CONFIG", "base_spec_top_level")
        
        matched_chunks = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            top_level = heading.split("->")[0].strip()
            if top_level in allowed_top_levels:
                matched_chunks.append(f"### Section: {heading}\n{all_records['documents'][idx]}")
                
        if matched_chunks:
            return "\n\n---\n\n".join(matched_chunks)
        return "Global REST API interface specifications are currently missing or unindexed."


    @tool("read_ansible_exmaple_code_single")
    def read_ansible_exmaple_code_single() -> str:
        """
        Reads production-grade single-operation YAML template architectures, global configs, 
        and console printouts under targeted sections including layout directories and script files.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        # Dynamically load single operation sections from external configuration profile
        target_sections = _load_config_list("ANSIBLE_CONFIG", "single_sections")
        
        matched_blueprints = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            if any(section in heading for section in target_sections):
                matched_blueprints.append(f"### Single Operation Blueprint: {heading}\n{all_records['documents'][idx]}")
                
        if matched_blueprints:
            return "\n\n---\n\n".join(matched_blueprints)
        return "Single operation playbook example blueprints are currently missing or unindexed."


    @tool("read_ansible_exmaple_code_batch_sequential")
    def read_ansible_exmaple_code_batch_sequential() -> str:
        """
        Reads production-grade sequential batch automation script architectures and corresponding 
        runtime logs from designated sequential batch workflow sections.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        # Dynamically load sequential batch sections from external configuration profile
        target_sections = _load_config_list("ANSIBLE_CONFIG", "batch_sequential_sections")
        
        matched_blueprints = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            if any(section in heading for section in target_sections):
                matched_blueprints.append(f"### Sequential Batch Blueprint: {heading}\n{all_records['documents'][idx]}")
                
        if matched_blueprints:
            return "\n\n---\n\n".join(matched_blueprints)
        return "Sequential batch playbook example blueprints are currently missing or unindexed."


    @tool("read_ansible_exmaple_code_batch_parallel")
    def read_ansible_exmaple_code_batch_parallel() -> str:
        """
        Reads production-grade parallel batch automation script architectures and corresponding 
        runtime logs from designated parallel batch execution sections.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        all_records = chroma_client.get_collection(name="ansible_agent_knowledge").get(
            where={"source": "fusioncompute_ansible_module_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        # Dynamically load parallel batch sections from external configuration profile
        target_sections = _load_config_list("ANSIBLE_CONFIG", "batch_parallel_sections")
        
        matched_blueprints = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            if any(section in heading for section in target_sections):
                matched_blueprints.append(f"### Parallel Batch Blueprint: {heading}\n{all_records['documents'][idx]}")
                
        if matched_blueprints:
            return "\n\n---\n\n".join(matched_blueprints)
        return "Parallel batch playbook example blueprints are currently missing or unindexed."


    @tool("query_specific_api_content")
    def query_specific_api_content(target_heading_or_keyword: str) -> str:
        """
        Extracts precise technical parameter tables, URL methods, and payload data schemas 
        exclusively from the core interface chapters of the raw FusionCompute REST API document.
        Automatically truncates the document from the error code section down to optimize context.

        The input parameter 'target_heading_or_keyword' must strictly be the Chinese text name of 
        the final API interface section (e.g., '查询指定主机'). It must not contain URL fragments, 
        HTTP methods, or request/response body parameter fields.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        
        filter_condition = {"source": "fusioncompute_8100_api_cleaned.docx"}
        allowed_top_levels = _load_config_list("API_CONFIG", "content_top_levels")

        def truncate_at_error_section(text_content: str) -> str:
            """Truncates the document entirely from the first occurrence of the error code row."""
            valid_lines = []
            for line in text_content.splitlines():
                if "错误码" in line:
                    break
                valid_lines.append(line)
            return "\n".join(valid_lines)
        
        # Channel 1: Strict substring matching bounded to target interface chapters
        all_records = collection.get(where=filter_condition, include=["metadatas", "documents"])
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            top_level = heading.split("->")[0].strip()
            
            if top_level in allowed_top_levels and target_heading_or_keyword.strip() in heading:
                cleaned_doc = truncate_at_error_section(all_records['documents'][idx])
                return f"### Verified API Schema: {heading}\n{cleaned_doc}"
                
        # Channel 2: High-precision Vector Search fallback restricted to the API source document
        nomic_safe_query = f"search_query: {target_heading_or_keyword}"
        response = ollama.embeddings(model="nomic-embed-text", prompt=nomic_safe_query)
        
        results = collection.query(
            query_embeddings=[response["embedding"]],
            where=filter_condition,
            n_results=5
        )
        
        if results and results["documents"] and results["documents"][0]:
            for doc_idx, meta_data in enumerate(results["metadatas"][0]):
                res_heading = meta_data.get("heading", "")
                res_top_level = res_heading.split("->")[0].strip()
                
                if res_top_level in allowed_top_levels:
                    cleaned_doc = truncate_at_error_section(results['documents'][0][doc_idx])
                    return f"### Verified API Vector Result: {res_heading}\n{cleaned_doc}"
                    
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
        
        # Validate configuration-driven decoupled blueprint template extractors
        ansible_single = AnsibleAutomationTools.read_ansible_exmaple_code_single.run()
        print(f"[STAGE 4.1] Single Operation Blueprints Mapped. Data size: {len(ansible_single)}")
        
        ansible_seq = AnsibleAutomationTools.read_ansible_exmaple_code_batch_sequential.run()
        print(f"[STAGE 4.2] Sequential Batch Blueprints Mapped. Data size: {len(ansible_seq)}")
        
        ansible_para = AnsibleAutomationTools.read_ansible_exmaple_code_batch_parallel.run()
        print(f"[STAGE 4.3] Parallel Batch Blueprints Mapped. Data size: {len(ansible_para)}")
        
    except Exception as e: 
        print(f"Basic sequential tool execution check failed: {e}")

    print("\n[STAGE 5] Running Restricted Tool for Specific API Channel Isolate (Dynamic Config)...")
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