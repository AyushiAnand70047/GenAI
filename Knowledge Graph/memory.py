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
    
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "mem0"

    # Check if collection already exists
    collections = [c.name for c in client.get_collections().collections]
    if collection_name in collections:
        print(f"Collection '{collection_name}' already exists, skipping creation.")
        return

    # Create new collection if it does not exist
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    print(f"Created new collection '{collection_name}' with 768 dimensions")

setup_qdrant_collection()

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "gemini",
        "config": {"api_key": GOOGLE_API_KEY, "model": "models/text-embedding-004"}
    },
    "llm": {"provider": "gemini", "config": {"api_key": GOOGLE_API_KEY, "model": "gemini-2.0-flash-exp"}},
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
    
    # Extract vector memories
    memories = "\n".join([m["memory"] for m in mem_result.get("results", [])])

    # Extract relations (from Neo4j graph)
    relations = "\n".join([
        f"{r['source']} -[{r['relationship']}]-> {r['destination']}"
        for r in mem_result.get("relations", [])
    ])

    print("memory ", memories)
    print("relations ", relations)

    SYSTEM_PROMPT = f"""
    You are a Memory-Aware Fact Extraction Agent.
    Use both vector memories and graph relations to answer.
    
    Vector Memories:
    {memories}

    Graph Relations:
    {relations}

    Answer the user clearly, using these memories if relevant.
    If a name or full name exists in relations, you should state it.
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]

    result = openai_client.chat.completions.create(
        model="gemini-2.0-flash-exp",
        messages=messages
    )

    assistant_reply = result.choices[0].message.content

    # Store just the clean assistant reply in memory (not full chat history)
    mem_client.add({"role": "assistant", "content": assistant_reply}, user_id="a123")

    return assistant_reply


while True:
    message = input(">> ")
    print("🤖: ", chat(message=message))