from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from memory import save_memory

# Set up Mistral
llm = Ollama(model="mistral")

print("📚 Welcome to your next WALTER.AI lesson!")
topic = input("🔍 What specific topic are you ready to dive into today?\n(e.g., 'Using GROUP BY in SQL' or 'Basic Regression in Python')\n> ").strip()

# Prompt the LLM with a warm, supportive tone and project-based learning structure
lesson_prompt = PromptTemplate(
    input_variables=["topic"],
    template="""
You're an engaging and approachable data instructor helping a learner understand: "{topic}"

Your job is to teach this topic in a way that's:
- Friendly, human, and motivating (think: a really helpful coach or mentor)
- Hands-on and project-based (we're building toward something real)
- Step-by-step (explain like you're sitting next to the learner)

Structure your response like this:

=== 🧠 Concept ===
Explain the topic in simple terms using real-world analogies. Keep it fun and easy to understand.

=== 🛠️ Step-by-Step Walkthrough ===
Provide a code example the learner can run and follow along with. Include brief explanations between steps.

=== 🚀 Your Mini Project Challenge ===
Design a short, meaningful task the learner can try based on what they just learned. This should feel like they're contributing to a bigger real-world project.

=== ✅ What Success Looks Like ===
Show an example of what the final result should look like. Keep it encouraging!

Use your tone to keep things warm, casual, and confidence-boosting — like Walter Shields would!
"""
)

# Run the prompt
chain = lesson_prompt | llm
lesson = chain.invoke({"topic": topic})

# Save lesson to memory
save_memory(lesson, metadata={"topic": topic, "type": "lesson"})

# Show the lesson to the learner
print("\n🎓 Here's your guided lesson:\n")
print(lesson)
