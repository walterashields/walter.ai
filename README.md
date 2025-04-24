# 📚 WALTER.AI – Personalized Learning Platform for Data Careers

WALTER.AI is an AI-powered, beginner-friendly learning platform that creates fully personalized learning paths and lesson content in data analytics, data science, and data engineering. 
Inspired by world-class training programs like the Google Data Analytics Certificate and Microsoft’s open-source curriculum, 
this system helps learners go from zero to job-ready through guided, interactive lessons.

## 🚀 What It Does

- 🔐 **Login-based onboarding** with learner-specific preferences and motivations
- 🎯 **Dynamic learning paths** tailored to skill level, learning style, and time commitment
- 📘 **Lessons generated with AI**, aligned to industry standards and scaffolded for beginners
- 💬 **Interactive challenge feedback** (code, multiple-choice, open-ended)
- 📊 **Dashboard view** to monitor lesson & track progress
- 🧠 **Memory system** that tracks user progress and completed lessons
- ✅ **Multi-format challenges** reviewed by GPT (code, quizzes, reflections)
- 🌐 Currently runs locally using **Ollama + Mistral** and **LangChain**

## 🛠️ Tech Stack

| Tool               | Purpose                                   |
|--------------------|-------------------------------------------|
| **Streamlit**      | Frontend & app framework                  |
| **LangChain**      | LLM orchestration                         |
| **Ollama (Mistral)** | Local LLM backend                         |
| **ChromaDB**       | Vector storage for lesson context         |
| **OpenAI Embeddings** | Used for document similarity (text-embedding-ada-002) |
| **Custom Prompt Engineering** | Structured lesson generation & feedback          |

## 🧪 How to Run It Locally

1. **Clone this repo**  
   ```bash
   git clone https://github.com/walterashields/walter.ai.git
   cd walter.ai

Set up your virtual environment

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Run Streamlit
streamlit run app.py
Open http://localhost:8501 in your browser.

⚠️ Ensure Ollama is installed and running with the Mistral model.
https://ollama.com

🧠 Personalization Flow
Learners are onboarded via three-step questions: background, learning style, and goals

A custom curriculum is generated based on responses

Lessons are generated on demand when clicked

Challenges are evaluated via LLM and marked complete after submission

✨ Features In Progress
Export completed lessons to Markdown/PDF

Multi-user deployment (currently in closed beta)

Public-facing hosted deployment via Streamlit Cloud or FastAPI backend

GitHub-based portfolio publishing

📁 Folder Structure
.
├── app.py                    # Main dashboard + onboarding
├── pages/
│   └── _lesson_runner.py     # Dynamic lesson loading and feedback
├── walter_memory/           # Stores learner profiles and progress
├── vector_store_openai/     # Chroma vector DB with embedded context
├── requirements.txt
├── README.md
🤝 Acknowledgments
Microsoft’s Data-Science-For-Beginners

Google’s Data Analytics Certificate

OpenAI and LangChain teams

Community feedback & beta testers 🙌

Created with ❤️ by @walterashields






