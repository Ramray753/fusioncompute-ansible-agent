import chromadb

def list_all_stored_keys():
    # Connect to the local persistent ChromaDB storage
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        # Access the specifically named collection for the Ansible Agent
        collection = chroma_client.get_collection(name="ansible_agent_knowledge")
    except Exception as e:
        print(f"[ERROR] Collection not found. Please run ingest.py first. Details: {e}")
        return

    # Critical optimization: Retrieve ONLY metadatas to save MacBook memory
    db_content = collection.get(include=["metadatas"])
    metadatas = db_content.get("metadatas", [])
    total_keys = len(metadatas)
    
    print("\n" + "="*20 + " CHROMADB KEY AUDIT REPORT " + "="*20)
    print(f"Total atomic Keys (Headings) indexed in local storage: {total_keys}")
    print("=" * 67 + "\n")
    
    if total_keys == 0:
        print("The database is currently empty.")
        return

    # Enumerate and print each inherited hierarchical key path
    for i, meta in enumerate(metadatas):
        source_file = meta.get("source", "Unknown File")
        api_heading = meta.get("heading", "Missing Heading Title")
        print(f"[{i+1:03d}] [Source: {source_file}] -> Key: {api_heading}")
        
    print("\n" + "="*27 + " END OF REPORT " + "="*27)

if __name__ == "__main__":
    list_all_stored_keys()