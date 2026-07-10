import chromadb
import ollama

# Connect to the existing local persistent DB
chroma_client = chromadb.PersistentClient(path="../chroma_db")
collection = chroma_client.get_collection(name="ansible_agent_knowledge")

# Prompt for testing
user_query = input("Enter the Ansible module or API keyword you want to test: ")

print("\n--- Searching for exact structural routing match... ---")
# Fetch all metadata records to execute deterministic keyword routing fallback
all_records = collection.get(include=["metadatas", "documents"])
matched_documents = []
matched_metadata = []

for idx, meta in enumerate(all_records.get("metadatas", [])):
    heading_path = meta.get("heading", "")
    # Check if the user query text directly cuts into the title key path
    if user_query in heading_path:
        matched_documents.append(all_records["documents"][idx])
        matched_metadata.append(meta)

# --- ROUTING DECISION LAYER ---
if matched_documents:
    print(f"[ROUTE DETERMINED] Found {len(matched_documents)} exact heading keyword matches. Bypassing vector approximations.")
    print("\n--- Top Most Relevant Knowledge Base Snippets ---")
    for i in range(min(2, len(matched_documents))):
        print(f"\n[Result {i+1}] Source File: {matched_metadata[i]['source']} | Section: {matched_metadata[i]['heading']}")
        print("-" * 60)
        print(matched_documents[i])
        print("-" * 60)
else:
    print("[ROUTE DETERMINED] No exact heading match found. Falling back to Cosine Vector Search.")
    
    # Prepend the mandatory Nomic task instruction prefix
    nomic_safe_query = f"search_query: {user_query}"
    response = ollama.embeddings(model="nomic-embed-text", prompt=nomic_safe_query)
    query_embedding = response["embedding"]
    
    # Query ChromaDB leveraging the newly synced Cosine graph space
    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    
    print("\n--- Top 2 Semantically Relevant Knowledge Base Snippets ---")
    if results and results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            print(f"\n[Result {i+1}] Source File: {results['metadatas'][0][i]['source']} | Section: {results['metadatas'][0][i].get('heading', 'N/A')}")
            print("-" * 60)
            print(doc)
            print("-" * 60)
    else:
        print("No relevant API or module definitions found.")