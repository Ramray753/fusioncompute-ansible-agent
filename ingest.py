import os
import glob
import logging
import re
import docx
import chromadb
import ollama

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_heading_level(p):
    style_name = p.style.name
    match = re.search(r'(?:Heading|标题)\s*(\d+)', style_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    text_stripped = p.text.strip()
    heading_num_match = re.match(r'^(\d+(?:\.\d+)+)\s+', text_stripped)
    if heading_num_match:
        num_str = heading_num_match.group(1)
        return num_str.count('.') + 1
        
    return None

def extract_hierarchical_leaf_sections(file_path):
    doc = docx.Document(file_path)
    sections = []
    current_hierarchy = {}
    
    current_section = {
        "path": "Initialization Context",
        "level": 0,
        "pieces": []
    }
    sections.append(current_section)
    
    heading_pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+(.*)$')
    
    for element in doc.element.body:
        if element.tag.endswith('p'):
            p = docx.text.paragraph.Paragraph(element, doc)
            text = p.text.strip()
            if not text:
                continue
                
            level = get_heading_level(p)
            if level is not None and level <= 4:
                current_hierarchy[level] = text
                levels_to_clear = [k for k in current_hierarchy.keys() if k > level]
                for lvl in levels_to_clear:
                    del current_hierarchy[lvl]
                
                path_pieces = [current_hierarchy[k] for k in sorted(current_hierarchy.keys())]
                full_path = " -> ".join(path_pieces)
                
                current_section = {
                    "path": full_path,
                    "level": level,
                    "pieces": [f"### Path: {full_path}\n"]
                }
                sections.append(current_section)
            else:
                current_section["pieces"].append(text)
                
        elif element.tag.endswith('tbl'):
            t = docx.table.Table(element, doc)
            table_lines = [""]
            for i, row in enumerate(t.rows):
                cells_text = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
                row_str = "| " + " | ".join(cells_text) + " |"
                table_lines.append(row_str)
                if i == 0:
                    separator = "| " + " | ".join(["---"] * len(cells_text)) + " |"
                    table_lines.append(separator)
            table_lines.append("")
            current_section["pieces"].append("\n".join(table_lines))
            
    leaf_sections = []
    total_extracted = len(sections)
    
    for i, sec in enumerate(sections):
        if sec["path"] == "Initialization Context":
            if sec["pieces"]:
                leaf_sections.append({
                    "path": sec["path"],
                    "content": "\n\n".join(sec["pieces"])
                })
            continue
            
        is_leaf = False
        if i == total_extracted - 1:
            is_leaf = True
        else:
            next_sec = sections[i + 1]
            if next_sec["level"] <= sec["level"]:
                is_leaf = True
                
        if is_leaf:
            leaf_sections.append({
                "path": sec["path"],
                "content": "\n\n".join(sec["pieces"])
            })
            
    return leaf_sections

def initialize_vector_db(db_path="./chroma_db", collection_name="ansible_agent_knowledge"):
    """
    Initializes ChromaDB collection with strict Cosine Space optimization.
    """
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    # 🎯 CRITICAL FIX: Force ChromaDB to use Cosine Similarity distance instead of L2
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def embed_and_store_sections(collection, sections, file_name, batch_size=50):
    logger.info(f"Executing KV-style injection for: {file_name}")
    b_ids, b_embeddings, b_documents, b_metadatas = [], [], [], []
    total_sections = len(sections)
    
    for i, sec in enumerate(sections):
        try:
            pure_kv_key = sec['path']
            nomic_safe_key = f"search_document: {pure_kv_key}"
            
            response = ollama.embeddings(model="nomic-embed-text", prompt=nomic_safe_key)
            embedding = response["embedding"]
            
            b_ids.append(f"{file_name}_leaf_{i}")
            b_embeddings.append(embedding)
            b_documents.append(sec['content'])
            b_metadatas.append({"heading": pure_kv_key, "source": file_name})
            
            if len(b_ids) == batch_size or (i + 1) == total_sections:
                collection.upsert(
                    ids=b_ids,
                    embeddings=b_embeddings,
                    documents=b_documents,
                    metadatas=b_metadatas
                )
                logger.info(f"Database sync: Logged leaf segments up to index {i}/{total_sections}")
                b_ids, b_embeddings, b_documents, b_metadatas = [], [], [], []
                
        except Exception as e:
            logger.error(f"Execution terminated at section index {i}: {str(e)}")
            raise e

def main():
    docs_dir = "./docs"
    docx_files = glob.glob(os.path.join(docs_dir, "*.docx"))
    if not docx_files:
        logger.warning(f"No source material found in target directory: {docs_dir}")
        return
        
    collection = initialize_vector_db()
    for file_path in docx_files:
        file_name = os.path.basename(file_path)
        try:
            sections = extract_hierarchical_leaf_sections(file_path)
            embed_and_store_sections(collection, sections, file_name)
            logger.info(f"KV Ingestion successful for file: {file_name}\n" + "-"*60)
        except Exception as e:
            logger.error(f"Data migration aborted for file {file_name}: {str(e)}")

if __name__ == "__main__":
    main()