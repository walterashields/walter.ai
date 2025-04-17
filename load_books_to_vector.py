from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# Step 1: Define your PDF files
pdf_paths = [
    "/Users/waltershields/Downloads/BooksToVector/analytics-made-accessible.pdf",
    "/Users/waltershields/Downloads/BooksToVector/Python-for-Data-Analysis.pdf",
    "/Users/waltershields/Downloads/BooksToVector/Fundamentals of Data Engineering.pdf"
]


# Step 2: Load and split content
all_chunks = []
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " "]
)

for path in pdf_paths:
    print(f"🔍 Loading: {path}")
    loader = PyPDFLoader(path)
    pages = loader.load()
    chunks = splitter.split_documents(pages)
    
    # Add metadata to help us track source
    for chunk in chunks:
        chunk.metadata["source"] = os.path.basename(path)
    all_chunks.extend(chunks)

print(f"✅ Loaded and split {len(all_chunks)} total chunks.")

import pickle

with open("split_chunks.pkl", "wb") as f:
    pickle.dump(all_chunks, f)

print("🧠 Chunks saved to split_chunks.pkl")

