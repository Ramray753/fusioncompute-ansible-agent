import os
import yaml
import urllib.parse
import chromadb
import ollama

# Establish absolute project root directory anchor (up two levels from mcp/mcp_resources.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Connection Singleton securely anchored to project root directory to prevent SQLite file-locks
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_DIR)
KNOWLEDGE_COLLECTION = CHROMA_CLIENT.get_collection(name="ansible_agent_knowledge")

def _load_config_list(section: str, config_key: str) -> list[str]:
    """
    Helper function to dynamically read interface classification lists from the 
    new YAML configuration file located inside the centralized 'conf/' folder.
    Supports robust fallback logic between .yaml and .yml extensions.
    """
    config_file = os.path.join(BASE_DIR, "conf", "ability.yaml")
    if not os.path.exists(config_file):
        config_file = os.path.join(BASE_DIR, "conf", "ability.yml")
        
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"[FATAL ERROR] Centralized configuration asset '{config_file}' is missing from workplace.")
    
    with open(config_file, "r", encoding="utf-8") as file_handle:
        try:
            config_data = yaml.safe_load(file_handle)
        except Exception as error:
            raise ValueError(f"[PARSING ERROR] Failed to parse YAML file {config_file}. Details: {str(error)}")
            
    try:
        # Enforce case-insensitive alignment to safely map old INI strings to lowercase YAML maps
        sec_key = section.lower()
        val_key = config_key.lower()
        
        if config_data and sec_key in config_data and val_key in config_data[sec_key]:
            raw_val = config_data[sec_key][val_key]
            if isinstance(raw_val, list):
                return [str(v).strip() for v in raw_val if str(v).strip()]
            elif isinstance(raw_val, str):
                return [v.strip() for v in raw_val.split(",") if v.strip()]
        return []
    except Exception as error:
        raise KeyError(f"[CONFIG ERROR] Failed to extract '{config_key}' from section '{section}'. Details: {str(error)}")

def _truncate_at_error_section(text_content: str) -> str:
    """Optimizes context window size by truncating payload at error code blocks."""
    valid_lines = []
    for line in text_content.splitlines():
        if "错误码" in line:
            break
        valid_lines.append(line)
    return "\n".join(valid_lines)

def fetch_api_headings() -> str:
    """Core logic to fetch filtered technical section headings reusing the global connection singleton."""
    all_records = KNOWLEDGE_COLLECTION.get(
        where={"source": "fusioncompute_8100_api_cleaned.docx"},
        include=["metadatas"],
        limit=1000
    )
    
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

def fetch_ansible_example(target_sections_key: str, section_label: str) -> str:
    """Core logic to pull designated standard playbook sample architectures from vector store."""
    all_records = KNOWLEDGE_COLLECTION.get(
        where={"source": "fusioncompute_ansible_module_cleaned.docx"},
        include=["metadatas", "documents"],
        limit=1000
    )
    
    target_sections = _load_config_list("ANSIBLE_CONFIG", target_sections_key)
    matched_blueprints = []
    for idx, meta in enumerate(all_records.get("metadatas", [])):
        heading = meta.get("heading", "")
        if any(section in heading for section in target_sections):
            matched_blueprints.append(f"### {section_label} Blueprint: {heading}\n{all_records['documents'][idx]}")
            
    if matched_blueprints:
        return "\n\n---\n\n".join(matched_blueprints)
    return f"{section_label} playbook blueprints are currently missing or unindexed."

def fetch_global_spec(config_key: str, source_file: str) -> str:
    """Core logic to extract baseline protocol specifications under allowed chapters."""
    all_records = KNOWLEDGE_COLLECTION.get(
        where={"source": source_file},
        include=["metadatas", "documents"],
        limit=1000
    )
    
    section_name = "API_CONFIG" if source_file.endswith("api_cleaned.docx") else "ANSIBLE_CONFIG"
    allowed_top_levels = _load_config_list(section_name, config_key)
    
    matched_chunks = []
    for idx, meta in enumerate(all_records.get("metadatas", [])):
        heading = meta.get("heading", "")
        if heading.split("->")[0].strip() in allowed_top_levels:
            matched_chunks.append(f"### Section: {heading}\n{all_records['documents'][idx]}")
            
    if matched_chunks:
        return "\n\n---\n\n".join(matched_chunks)
    return f"Global specifications for '{config_key}' are missing or unindexed."

def query_api_content_hybrid(keyword: str) -> str:
    """Executes high-precision dual-channel routing fallback for target Chinese schema endpoints."""
    decoded_keyword = urllib.parse.unquote(keyword).strip()
    
    filter_condition = {"source": "fusioncompute_8100_api_cleaned.docx"}
    allowed_top_levels = _load_config_list("API_CONFIG", "content_top_levels")

    # Channel 1: Strict Substring Lookup over fully loaded records
    all_records = KNOWLEDGE_COLLECTION.get(where=filter_condition, include=["metadatas", "documents"], limit=1000)
    for idx, meta in enumerate(all_records.get("metadatas", [])):
        heading = meta.get("heading", "")
        if heading.split("->")[0].strip() in allowed_top_levels and decoded_keyword in heading:
            cleaned_doc = _truncate_at_error_section(all_records['documents'][idx])
            return f"### Verified API Schema: {heading}\n{cleaned_doc}"
            
    # Channel 2: Cleaned Vector Fallback using fully restored Chinese semantic strings
    nomic_safe_query = f"search_query: {decoded_keyword}"
    response = ollama.embeddings(model="nomic-embed-text", prompt=nomic_safe_query)
    results = KNOWLEDGE_COLLECTION.query(query_embeddings=[response["embedding"]], where=filter_condition, n_results=5)
    
    if results and results["documents"] and results["documents"][0]:
        for doc_idx, meta_data in enumerate(results["metadatas"][0]):
            res_heading = meta_data.get("heading", "")
            if res_heading.split("->")[0].strip() in allowed_top_levels:
                cleaned_doc = _truncate_at_error_section(results['documents'][0][doc_idx])
                return f"### Verified API Vector Result: {res_heading}\n{cleaned_doc}"
                    
    return f"No certified data specification discovered within core API chapters matching: '{decoded_keyword}'."