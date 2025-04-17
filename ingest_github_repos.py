import os
import json
import chromadb
import markdown2
import nbformat
from chromadb.utils import embedding_functions

REPO_PATH = "./repos"
CHROMA_PATH = "./chromadb_repo"
collection_name = "repo_chunks"

# Setup Chroma DB
chroma_client = chromadb.PersistentClient(path="./chromadb_repo")
if collection_name in [c.name for c in chroma_client.list_collections()]:
    chroma_client.delete_collection(collection_name)
collection = chroma_client.create_collection(name=collection_name)

def chunk_text(text, max_tokens=500):
    # Simple chunking by paragraphs
    paragraphs = text.split('\n\n')
    chunks, current = [], ""
    for para in paragraphs:
        if len(current + para) > max_tokens:
            chunks.append(current.strip())
            current = para + "\n\n"
        else:
            current += para + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks

def load_and_clean_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return markdown2.markdown(f.read())

def load_and_clean_ipynb(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
        return "\n".join(cell['source'] for cell in nb.cells if cell.cell_type == 'markdown')

def load_and_clean_py(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def ingest_repo(repo_folder):
    for root, _, files in os.walk(repo_folder):
        for file in files:
            ext = os.path.splitext(file)[1]
            file_path = os.path.join(root, file)
            repo_name = os.path.basename(repo_folder)
            if ext in ['.md', '.ipynb', '.py']:
                try:
                    if ext == '.md':
                        raw = load_and_clean_md(file_path)
                    elif ext == '.ipynb':
                        raw = load_and_clean_ipynb(file_path)
                    elif ext == '.py':
                        raw = load_and_clean_py(file_path)
                    else:
                        continue

                    chunks = chunk_text(raw)
                    for i, chunk in enumerate(chunks):
                        collection.add(
                            documents=[chunk],
                            metadatas=[{
                                "repo": repo_name,
                                "file": file,
                                "chunk": i
                            }],
                            ids=[f"{repo_name}_{file}_{i}"]
                        )
                except Exception as e:
                    print(f"❌ Failed to process {file_path}: {e}")

# Run ingestion on all repos
for repo in os.listdir(REPO_PATH):
    print(f"📥 Ingesting: {repo}")
    ingest_repo(os.path.join(REPO_PATH, repo))


print("✅ All repos ingested into Chroma!")


