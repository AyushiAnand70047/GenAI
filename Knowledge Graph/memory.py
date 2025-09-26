from mem0 import Memory
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

GOOGLE_API_KEY = ""
QUADRANT_HOST = "localhost"
NEO4J_URI="bolt://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD=""

def setup_qdrant_collection():
    """Setup Qdrant collection with correct dimensions for Gemini embedding"""
    # Connect to your Docker Qdrant instance
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "mem0"  # Default collection name used by mem0
    
    try:
        # Try to delete existing collection if it exists
        client.delete_collection(collection_name=collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception as e:
        print(f"Collection might not exist or already deleted: {e}")
    
    # Create new collection with 768 dimensions for Gemini text-embedding-004
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    print(f"Created new collection '{collection_name}' with 768 dimensions")

# Setup collection before initializing mem0 - this connects to your Docker container
setup_qdrant_collection()

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "gemini",
        "config": {"api_key": GOOGLE_API_KEY, "model": "models/text-embedding-004"}
    },
    "llm": {"provider": "gemini", "config": {"api_key": GOOGLE_API_KEY, "model": "gemini-2.0-flash-001"}},
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QUADRANT_HOST,
            "port": 6333
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {"url": NEO4J_URI, "username": NEO4J_USERNAME, "password": NEO4J_PASSWORD}
    }
}

mem_client = Memory.from_config(config)
openai_client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def chat(message):
    mem_result = mem_client.search(query=message, user_id="a123")
    print("memory ", mem_result)
    
    messages = [
        {"role": "user", "content": message}
    ]
    
    result = openai_client.chat.completions.create(
        model="gemini-2.0-flash-exp",  # Fixed model name
        messages=messages
    )
    
    messages.append(
        {"role": "assistant", "content": result.choices[0].message.content}
    )
    
    mem_client.add(messages, user_id="a123")
    
    return result.choices[0].message.content

while True:
    message = input(">> ")
    print("🤖: ", chat(message=message))
