
import os
import json
# Ensure memory folder exists
os.makedirs("memory", exist_ok=True)
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


# Memory location
MEMORY_FOLDER = "walter_memory"
PROFILE_FILE = os.path.join(MEMORY_FOLDER, "learner_profile.json")

# Ensure memory folder exists
os.makedirs(MEMORY_FOLDER, exist_ok=True)

# Embedding model from Ollama
embedding_function = OllamaEmbeddings(model="mistral")

# Initialize Chroma vector store
vectorstore = Chroma(
    persist_directory=MEMORY_FOLDER,
    embedding_function=embedding_function
)

# Create a retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


# ----------- 🔍 Save / Load Learner Profile -----------

def save_learner_profile(profile: dict):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f)


def load_learner_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return None


# ----------- 🧠 Save Session Summary to Vector Store -----------

import hashlib
import time

def save_memory(content, metadata):
    os.makedirs("memory", exist_ok=True)  # Ensure folder exists

    hash_id = hashlib.md5((content + str(time.time())).encode()).hexdigest()[:8]
    entry_type = metadata.get("type", "entry")
    filename = f"memory/{entry_type}_{hash_id}.json"

    try:
        with open(filename, "w") as f:
            json.dump({
                "content": content,
                "metadata": metadata
            }, f, indent=2)
        print(f"✅ Saved to memory: {filename}")
    except Exception as e:
        print(f"❌ Failed to save memory: {e}")


def retrieve_memory(query: str):
    return retriever.get_relevant_documents(query)

# ---- ✅ Track completed lessons ----

PROGRESS_FILE = os.path.join(MEMORY_FOLDER, "completed_lessons.json")

def mark_lesson_complete(topic):
    completed = []
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            completed = json.load(f)
    if topic not in completed:
        completed.append(topic)
        with open(PROGRESS_FILE, "w") as f:
            json.dump(completed, f)

def get_completed_lessons(memory_folder="walter_memory"):
    progress_file = os.path.join(memory_folder, "completed_lessons.json")
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            return json.load(f)
    return []
