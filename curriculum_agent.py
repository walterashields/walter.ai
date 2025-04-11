from memory import (
    load_learner_profile,
    save_learner_profile,
    save_memory,
    retrieve_memory
)

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

# Set up the local Mistral model
llm = Ollama(model="mistral")

# 🔍 Step 0: Check for existing learner profile
profile = load_learner_profile()

if profile:
    print("👋 Welcome back to WALTER.AI!")
    print(f"Last time, you chose the {profile['track']} track.")
    print("Would you like to continue where you left off?\n")

    resume = input("✅ Type 'yes' to continue, or 'no' to start fresh: ").strip().lower()

    if resume == "yes":
        print("\n🎯 Here's your last saved curriculum:\n")
        print(profile["curriculum"])
        exit()
    else:
        print("🌀 Okay — let’s start fresh.\n")

# 🧠 Step 1: Discovery - Ask learner a series of questions
print("👋 Hi! I’m WALTER.AI, your personalized AI learning coach.")
print("Let’s figure out your ideal path in data together. I’ll ask you a few quick questions.\n")

print("\n🧠 Let's get to know you so we can create a path that *actually fits* your style.\n")

# 1. Purpose (Why Now?)
interest = input("💬 What's driving your interest in learning data right now? (Feel free to be honest!)\n> ")

# 2. Past Experiences
tools = input("\n🛠️ Have you worked with any tools or tech before? (Excel, SQL, Python, or even just spreadsheets?)\n> ")

# 3. Imagined Future
future = input("\n🌟 Imagine 3 months from now, you’ve made big progress. What’s happening? What are you doing with your new skills?\n> ")

# 4. Learning Style
style = input("\n🎧 How do you like to learn best? (Step-by-step? Jump in and try? Watching first? Mixing it up?)\n> ")

# 5. Weekly Commitment
time = input("\n⏳ How much time each week can you realistically commit to learning?\n> ")

# 🎯 Step 2: Suggest learning paths
print("\nBased on what you shared, here are 3 potential tracks you might enjoy:\n")
print("📊 Data Analyst Track – Focus on Excel, SQL, and dashboards (e.g., Power BI).")
print("⚙️ Data Engineering Track – Learn Python, databases, and automation tools.")
print("🤖 Data Science Track – Explore Python, machine learning, and predictive modeling.\n")

track = input("🤔 Which track would you like to pursue? (Type: Analyst, Engineer, or Scientist): ").strip().lower()

# 📘 Step 3: Generate a curriculum based on selected track and learner profile
prompt_template = PromptTemplate(
    input_variables=["track", "interest", "tools", "future", "style", "time"],
    template="""
You are a friendly, expert data coach creating a personalized learning journey for a new learner. They want something that feels practical, encouraging, and fun — not overwhelming or academic.

Here’s what they shared:
- Why they want to learn: {interest}
- Past experience with tools: {tools}
- What they hope to achieve in 3 months: {future}
- How they prefer to learn: {style}
- Time available per week: {time}
- Chosen track: {track}

Your task:
- Determine a realistic number of weeks for their learning path based on their weekly time
- Design the path using learning psychology (e.g., spaced repetition, small wins, motivation)
- Break the curriculum into weeks that each focus on a mini-milestone toward a final project
- Make it fun, friendly, and clear — in a tone that sounds human and empowering

Output format:

Week 1:
- ...

Week 2:
- ...

(Continue as many weeks as needed for an achievable but meaningful outcome)
"""
)

chain = prompt_template | llm

output = chain.invoke({
    "track": track,
    "interest": interest,
    "tools": tools,
    "future": future,
    "style": style,
    "time": time
})

# 💾 Step 4: Save learner state and memory
learner_profile = {
    "track": track,
    "interest": interest,
    "tools": tools,
    "future": future,
    "style": style,
    "time": time,
    "curriculum": output
}

save_learner_profile(learner_profile)
save_memory(output, metadata={"track": track, "topic": "curriculum"})

# 🖥️ Step 5: Display the personalized curriculum
print("\n🎯 Here's your custom learning path:\n")
print(output)
