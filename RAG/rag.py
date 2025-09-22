from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore


pdf_path = Path(__file__).parent /"node-dev.pdf"

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

split_docs = text_splitter.split_documents(documents=docs)

embedder = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=""
)

vector_store = QdrantVectorStore.from_documents(
    documents=[],
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embedder
)

vector_store.add_documents(documents=split_docs)
print("Injection Done")

retriver = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embedder
)

relevant_chunks = retriver.similarity_search(
    query="What is fs module?"
)

SYSTEM_PROMPT = f"""
You are an helpful AI Assistant who responds base of the available context.

Context:
{relevant_chunks}
"""