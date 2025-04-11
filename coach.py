from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from memory import save_memory

# Load local LLM
llm = Ollama(model="mistral")

print("🧑🏽‍🏫 WALTER.AI Coach Mode: Let’s review your code together!")

# Step 1: Ask for the topic
topic = input("\n📘 What topic or lesson is this code related to?\n> ").strip()

# Step 2: Ask for the learner’s code
print("\n💻 Paste your code below. When you're done, type 'END' on a new line:")
code_lines = []
while True:
    line = input()
    if line.strip().lower() == "end":
        break
    code_lines.append(line)

submitted_code = "\n".join(code_lines)

# Step 3: Prompt for feedback
feedback_prompt = PromptTemplate(
    input_variables=["topic", "submitted_code"],
    template="""
You're a friendly and highly skilled data and code coach. A learner just completed a task on the topic: "{topic}"

Here’s their code:
{submitted_code}

Please review the code and respond with:
- Warm encouragement if it’s mostly correct
- Helpful, friendly feedback if there are mistakes
- Clear explanations of *why* something needs fixing (without sounding robotic)
- Suggestions for making it even better, if possible
- Use an encouraging, upbeat tone — like Walter Shields helping someone level up!

Structure your answer like this:

=== ✅ What You Did Well ===
...

=== ⚠️ Fixes & Suggestions ===
...

=== 💡 Pro Tips to Go Further ===
...
"""
)

chain = feedback_prompt | llm
feedback = chain.invoke({
    "topic": topic,
    "submitted_code": submitted_code
})

# Step 4: Save to memory
save_memory(feedback, metadata={"topic": topic, "type": "code_review"})

# Step 5: Show the feedback
print("\n🧠 Here's your feedback from WALTER.AI:\n")
print(feedback)