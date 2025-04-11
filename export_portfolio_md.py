import os
import json
import re

MEMORY_FOLDER = "memory"
EXPORT_FOLDER = "portfolio_markdown"

os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Collect lessons and feedback from memory
lessons = {}
feedbacks = {}

for filename in os.listdir(MEMORY_FOLDER):
    if filename.startswith("lesson_"):
        with open(os.path.join(MEMORY_FOLDER, filename)) as f:
            data = json.load(f)
            topic = data["metadata"].get("topic", "Unknown Topic")
            lessons[topic] = data["content"]

    elif filename.startswith("code_review_") or filename.startswith("retry_review_"):
        with open(os.path.join(MEMORY_FOLDER, filename)) as f:
            data = json.load(f)
            topic = data["metadata"].get("topic", "Unknown Topic")
            feedbacks.setdefault(topic, []).append(data["content"])

# Export to markdown
for i, topic in enumerate(lessons.keys(), 1):
    lesson = lessons[topic]
    topic_slug = re.sub(r'[^a-zA-Z0-9]+', '-', topic).strip("-").lower()

    filename = f"{EXPORT_FOLDER}/{i:02d}-{topic_slug}.md"

    with open(filename, "w") as f:
        f.write(f"# 📘 {topic}\n\n")
        f.write("## 🧠 Lesson Content\n\n")
        f.write(lesson.strip() + "\n\n")

        if topic in feedbacks:
            for j, fb in enumerate(feedbacks[topic], 1):
                f.write(f"## 👨🏽‍🏫 Feedback Round {j}\n\n")
                f.write(fb.strip() + "\n\n")

    print(f"✅ Exported: {filename}")

print("\n📁 All markdown files saved to /portfolio_markdown/")