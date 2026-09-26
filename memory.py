import chromadb

# Initialize persistent storage in local ./chroma_db folder
chroma_client = chromadb.PersistentClient(path="./chroma_db")
memory_collection = chroma_client.get_or_create_collection(name="jarvis_memory")


def store_memory(memory_id: str, fact: str, category: str = "general"):
    """Store a key contextual fact into vector database."""
    memory_collection.upsert(
        documents=[fact],
        metadatas=[{"category": category}],
        ids=[memory_id]
    )
    print(f"[Memory Saved]: '{fact}' under ID: {memory_id}")


def recall_memory(query: str, n_results: int = 3) -> list:
    """Perform semantic search across stored memories."""
    results = memory_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    docs = results.get("documents", [[]])[0]
    return docs if docs else []


if __name__ == "__main__":
    # Test saving and recalling memories
    store_memory("user_name", "The user's name is Deep Aditya.", category="identity")
    store_memory("creator_identity", "Jarvis was engineered, coded, and created by Deep Aditya.", category="identity")
    store_memory("gpu_spec", "The host PC runs an NVIDIA RTX 5050 GPU with 8GB VRAM.", category="hardware")

    store_memory("phone_spec", "The user's mobile phone model is AI+ Nova 2 Ultra.", category="hardware")

    print("\n--- Testing Semantic Search ---")
    memories = recall_memory("What graphics card is installed on this PC?")
    print(f"Recalled Knowledge: {memories}")