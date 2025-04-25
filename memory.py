
import os
import json
# Ensure memory folder exists
os.makedirs("memory", exist_ok=True)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from datetime import datetime
from langchain_core.messages import AIMessage  # add this near the top


import re


# Memory location
MEMORY_FOLDER = "walter_memory"

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



def make_serializable(obj):
    if isinstance(obj, AIMessage):
        return obj.content
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    return obj

def save_learner_profile(profile: dict, profile_path: str):
    with open(profile_path, "w") as f:
        json.dump(make_serializable(profile), f, indent=2)


def load_learner_profile(profile_path: str):
    if os.path.exists(profile_path):
        with open(profile_path, "r") as f:
            return json.load(f)
    return None


# ----------- 🧠 Save Session Summary to Vector Store -----------

import hashlib
import time

import uuid
import re
from datetime import datetime

def save_memory(content, metadata, memory_folder="walter_memory/default_user"):
    os.makedirs(memory_folder, exist_ok=True)

    # Clean topic for filename use
    safe_topic = re.sub(r"\W+", "_", metadata.get("topic", "note")).strip("_").lower()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # short unique ID to prevent collisions

    filename = f"{safe_topic}_{timestamp}_{unique_id}.txt"
    path = os.path.join(memory_folder, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Topic: {metadata.get('topic', '')}\n")
        f.write(f"# Type: {metadata.get('type', '')}\n\n")
        
        # Convert AIMessage to string if needed
        if isinstance(content, AIMessage):
            f.write(content.content)
        else:
            f.write(str(content))




def retrieve_memory(query: str):
    return retriever.get_relevant_documents(query)

# ---- ✅ Track completed lessons ----

PROGRESS_FILE = os.path.join(MEMORY_FOLDER, "completed_lessons.json")

def mark_lesson_complete(topic, memory_folder="walter_memory/default_user"):
    os.makedirs(memory_folder, exist_ok=True)
    completed_file = os.path.join(memory_folder, "completed_lessons.json")
    
    if os.path.exists(completed_file):
        with open(completed_file, "r", encoding="utf-8") as f:
            completed = json.load(f)
    else:
        completed = []

    if topic not in completed:
        completed.append(topic)
        with open(completed_file, "w", encoding="utf-8") as f:
            json.dump(completed, f, indent=2)


def get_completed_lessons(memory_folder="walter_memory/default_user"):
    completed_file = os.path.join(memory_folder, "completed_lessons.json")
    if not os.path.exists(completed_file):
        return []
    with open(completed_file, "r", encoding="utf-8") as f:
        return json.load(f)

