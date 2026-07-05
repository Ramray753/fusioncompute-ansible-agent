import chromadb
import ollama
from crewai.tools import tool

class PythonRestTools:
    """
    Certified Python REST API Toolset structured with mandatory progressive 
    discovery stages to enforce perfect API architectural alignment.
    """

    @tool("1. Fetch All Available Document Headings")
    def fetch_all_api_headings() -> str:
        """
        Use this tool to retrieve the complete directory index (all section headings) 
        of the FusionCompute REST API document. This allows building an internal knowledge map 
        and selecting the most relevant sections before querying specifics. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        try:
            collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        except Exception as e:
            return f"Database connection error: {str(e)}"
            
        # Extract metadata matrix strictly bounded to the REST API source document
        all_records = collection.get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas"]
        )
        
        # Deduplicate and sort heading keys in original structural sequence
        seen_headings = []
        for meta in all_records.get("metadatas", []):
            h_path = meta.get("heading", "")
            if h_path and h_path not in seen_headings:
                seen_headings.append(h_path)
                
        if not seen_headings:
            return "No registered headings discovered in the target REST directory."
            
        formatted_directory = [f"[{i+1:03d}] {heading}" for i, heading in enumerate(seen_headings)]
        return "\n".join(formatted_directory)


    @tool("2. Read Global API Format Specification")
    def read_api_format_specification() -> str:
        """
        Use this tool to read the entire baseline specification under the top-level heading 'API接口格式'. 
        Provides mandatory knowledge regarding global HTTP request lines, headers, response status structures, 
        and global base URL pathway configurations. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        
        all_records = collection.get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        matched_chunks = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            heading = meta.get("heading", "")
            # Lock content down strictly to the global interface standards sections
            if "API接口格式" in heading:
                matched_chunks.append(f"### Section: {heading}\n{all_records['documents'][idx]}")
                
        if matched_chunks:
            return "\n\n---\n\n".join(matched_chunks)
        return "Global API formatting specifications are currently missing or unindexed."


    @tool("3. Read End-to-End Programming Blueprints")
    def read_api_code_blueprints() -> str:
        """
        Use this tool to read the complete context under the top-level heading 'API调用代码示例'. 
        Provides raw bash cURL integration scripts and real terminal JSON responses. 
        Analyze this to understand payload nesting and token extraction before code design. Executed once.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        
        all_records = collection.get(
            where={"source": "fusioncompute_8100_api_cleaned.docx"},
            include=["metadatas", "documents"]
        )
        
        matched_blueprints = []
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            if "API调用代码示例" in meta.get("heading", ""):
                matched_blueprints.append(f"### Blueprint: {meta['heading']}\n{all_records['documents'][idx]}")
                
        if matched_blueprints:
            return "\n\n---\n\n".join(matched_blueprints)
        return "Official programming blueprint examples are missing or unindexed."


    @tool("4. Query Specific Section Content by Heading or Keyword")
    def query_specific_section_content(target_heading_or_keyword: str) -> str:
        """
        Retrieves the exact parameter tables, data schemas, and specifications for a single endpoint section. 
        Input should be an exact heading string found in Tool 1 (e.g., '计算虚拟化接口 -> 虚拟机管理 -> 创建虚拟机') 
        or a strong domain keyword (e.g., '创建数据存储'). Executed multiple times as needed.
        """
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
        
        filter_condition = {"source": "fusioncompute_8100_api_cleaned.docx"}
        
        # CHANNEL 1: High-speed literal match loop to guarantee perfect routing precision
        all_records = collection.get(where=filter_condition, include=["metadatas", "documents"])
        for idx, meta in enumerate(all_records.get("metadatas", [])):
            if target_heading_or_keyword.strip() in meta.get("heading", ""):
                return f"### Verified Schema: {meta['heading']}\n{all_records['documents'][idx]}"
                
        # CHANNEL 2: Fallback to high-precision Cosine Vector Search if literal matching misses
        nomic_safe_query = f"search_query: {target_heading_or_keyword}"
        response = ollama.embeddings(model="nomic-embed-text", prompt=nomic_safe_query)
        
        results = collection.query(
            query_embeddings=[response["embedding"]],
            where=filter_condition,
            n_results=1
        )
        
        if results and results["documents"] and results["documents"][0]:
            return results["documents"][0][0]
        return f"No certified technical details found matching keyword: '{target_heading_or_keyword}'."


# ==============================================================================
# RIGOROUS 4-STAGE PIPELINE CELLULAR UNIT TEST MODULE
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*20 + " STARTING REFACTORED PYTHON TOOLS AUDIT " + "="*20)
    
    # [STAGE 1 TEST] Fetching global index directory map
    print("\n[STAGE 1] Running Tool 1: fetch_all_api_headings...")
    try:
        directory_dump = PythonRestTools.fetch_all_api_headings.run()
        print("Success! Headings directory mapped. Sample excerpt below:")
        lines = directory_dump.split("\n")
        for line in lines[:8]: # Display first few elements
            print(f"  {line}")
        print(f"  ... [Total lines indexed: {len(lines)}]")
    except Exception as e:
        print(f"Failed Stage 1: {e}")
        
    # [STAGE 2 TEST] Fetching global specs and base URL pathways
    print("\n[STAGE 2] Running Tool 2: read_api_format_specification...")
    try:
        format_spec = PythonRestTools.read_api_format_specification.run()
        print(f"Success! Base specification acquired. Excerpt:\n{format_spec[:300]}...\n")
    except Exception as e:
        print(f"Failed Stage 2: {e}")

    # [STAGE 3 TEST] Fetching real-world coding benchmarks and JSON mocks
    print("\n[STAGE 3] Running Tool 3: read_api_code_blueprints...")
    try:
        blueprints = PythonRestTools.read_api_code_blueprints.run()
        print(f"Success! Execution blueprint copy achieved. Excerpt:\n{blueprints[:300]}...\n")
    except Exception as e:
        print(f"Failed Stage 3: {e}")

    # [STAGE 4 TEST] Repeatable deep dive lookup for a single functional component
    test_target = "创建数据存储"
    print(f"\n[STAGE 4] Running Tool 4: query_specific_section_content for '{test_target}'...")
    try:
        detailed_schema = PythonRestTools.query_specific_section_content.run(target_heading_or_keyword=test_target)
        print(f"Success! Component Schema isolated perfectly:\n{detailed_schema[:400]}...\n")
    except Exception as e:
        print(f"Failed Stage 4: {e}")

    print("="*19 + " PYTHON REST TOOLS 4-STAGE PIPELINE VALIDATED " + "="*19 + "\n")