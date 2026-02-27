import os
import glob
from mcp.server.fastmcp import FastMCP
import chromadb
from chromadb.utils import embedding_functions

# Initialize FastMCP Server
mcp = FastMCP("MemoryRAG")

# Setup ChromaDB persistent client
db_path = os.path.expanduser("~/.agent/memory-mcp/chroma_db")
os.makedirs(db_path, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=db_path)

# Use multilingual model so Indo-English queries map to the same semantic vector
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

def index_memory_files():
    memory_dir = os.path.expanduser("~/.agent/memory")
    if not os.path.exists(memory_dir):
        return 0

    files = glob.glob(os.path.join(memory_dir, "**/*.md"), recursive=True)
    
    docs = []
    ids = []
    metadatas = []
    
    # We chunk the markdown by '### Session:' headers to keep context intact
    doc_id = 0
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            sessions = content.split("### Session:")
            for s in sessions:
                s = s.strip()
                if not s: continue
                chunk = "### Session: " + s
                docs.append(chunk)
                ids.append(f"doc_{os.path.basename(file)}_{doc_id}")
                metadatas.append({"source": os.path.basename(file)})
                doc_id += 1
                
    if docs:
        try:
            chroma_client.delete_collection("session_memory")
        except Exception:
            pass # Collection doesn't exist yet
            
        collection = chroma_client.get_or_create_collection(
            name="session_memory", 
            embedding_function=sentence_transformer_ef
        )
        collection.add(documents=docs, ids=ids, metadatas=metadatas)
        return len(docs)
    return 0

@mcp.tool()
def search_memory(query: str, n_results: int = 3) -> str:
    """
    Search past declarative memory sessions using bilingual semantic search.
    Use this proactively to recall architectural decisions, previous errors, or blueprints.
    """
    # Simply re-index on every search to guarantee freshness (valid since dataset is very small)
    index_memory_files()
    
    collection = chroma_client.get_or_create_collection(
        name="session_memory", 
        embedding_function=sentence_transformer_ef
    )
    
    # Safe guard if collection is empty
    if collection.count() == 0:
        return "Memory bank is currently empty."

    # Prevent requesting more results than exist in DB
    actual_results = min(n_results, collection.count())
    results = collection.query(query_texts=[query], n_results=actual_results)
    
    if not results['documents'] or not results['documents'][0]:
        return "No relevant memory found."
        
    response = f"Found {len(results['documents'][0])} relevant memories:\n\n"
    for idx, doc in enumerate(results['documents'][0]):
        source = results['metadatas'][0][idx]['source']
        distance = results['distances'][0][idx] if 'distances' in results and results['distances'] else 'N/A'
        response += f"--- From {source} (Score: {distance}) ---\n{doc}\n\n"
        
    return response

if __name__ == "__main__":
    # Ensure master memory dir exists
    os.makedirs(os.path.expanduser("~/.agent/memory/topics"), exist_ok=True)
    
    # Start the MCP standard IO server
    mcp.run()
