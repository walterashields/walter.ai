from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import pickle
import os

# 🔁 Load pre-split chunks from disk
with open("split_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# 💡 Optional: Only use a subset for faster testing
chunks = chunks[:500]
print(f"📦 Embedding {len(chunks)} chunks...")

# 🔐 Load OpenAI embedding model
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

# 💾 Create Chroma vector store with OpenAI embeddings
CHROMA_DIR = "vector_store_openai"
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=CHROMA_DIR
)

vectorstore.persist()
print(f"✅ Stored {len(chunks)} chunks in {CHROMA_DIR}")
