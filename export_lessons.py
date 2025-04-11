import os
import json
from fpdf import FPDF
from memory import get_completed_lessons

# Where to look for stored memory files
MEMORY_FOLDER = "memory"
OUTPUT_FOLDER = "portfolio"

# Create output folder if needed
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load completed lesson titles
completed_lessons = get_completed_lessons()

# Load all memory files
if not os.path.exists(MEMORY_FOLDER):
    print("⚠️ No memory folder found. You must complete at least one lesson before exporting.")
    exit()

memory_files = os.listdir(MEMORY_FOLDER)
lesson_data = {}

for file in memory_files:
    path = os.path.join(MEMORY_FOLDER, file)
    with open(path, "r") as f:
        entry = json.load(f)
        topic = entry["metadata"].get("topic")
        type_ = entry["metadata"].get("type")

        if topic in completed_lessons:
            if topic not in lesson_data:
                lesson_data[topic] = {}
            lesson_data[topic][type_] = entry["content"]

# Sort lessons in the order they were completed
sorted_lessons = [t for t in completed_lessons if t in lesson_data]

# Export each lesson to a PDF
for i, topic in enumerate(sorted_lessons, 1):
    data = lesson_data[topic]

    lesson = data.get("lesson", "[No lesson found]")
    review = data.get("code_review", "[No feedback found]")

    # Create a PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Lesson {i}: {topic}", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "\n=== LESSON ===\n" + lesson.encode("ascii", "ignore").decode())
    pdf.multi_cell(0, 10, "\n=== COACH FEEDBACK ===\n" + review.encode("ascii", "ignore").decode())

    filename = f"{OUTPUT_FOLDER}/{str(i).zfill(2)} - {topic[:40]}.pdf"
    pdf.output(filename)

    print(f"✅ Exported: {filename}")

print("\n📁 All completed lessons exported to the /portfolio folder.")
