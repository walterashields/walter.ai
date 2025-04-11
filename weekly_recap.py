import os
import json
import datetime
from memory import (
    load_learner_profile,
    get_completed_lessons
)

MEMORY_FOLDER = "memory"

# === Load learner info
profile = load_learner_profile()
if not profile:
    print("❌ No learner profile found. Run curriculum_agent.py first.")
    exit()

curriculum = profile.get("curriculum", "")
all_lessons = [line.strip("- ").strip() for line in curriculum.splitlines() if line.strip().startswith("- ")]
completed = get_completed_lessons()

# === Helper: Check if a file was written this week
def is_this_week(filepath):
    try:
        timestamp = os.path.getmtime(filepath)
        dt = datetime.datetime.fromtimestamp(timestamp)
        today = datetime.datetime.now()
        return dt.isocalendar()[1] == today.isocalendar()[1]
    except:
        return False

# === Gather lesson completions this week
this_week = []
for filename in os.listdir(MEMORY_FOLDER):
    if filename.startswith("lesson_") and is_this_week(os.path.join(MEMORY_FOLDER, filename)):
        with open(os.path.join(MEMORY_FOLDER, filename)) as f:
            data = json.load(f)
            topic = data.get("metadata", {}).get("topic")
            if topic and topic not in this_week:
                this_week.append(topic)

# === Build recap message
print("\n📆 WEEKLY PROGRESS RECAP")
print("=" * 30)

if this_week:
    print("✅ Lessons Completed This Week:")
    for lesson in this_week:
        print(f" - {lesson}")
else:
    print("😅 No new lessons completed yet this week.")
    print("Let’s aim for 1 small win today!")

# === What’s Next
remaining = [l for l in all_lessons if l not in completed]
if remaining:
    print("\n🔜 Upcoming Lessons:")
    for l in remaining[:3]:
        print(f" - {l}")
else:
    print("\n🎉 You've completed the entire curriculum! Incredible work!")

# === Motivation Boost
print("\n💬 Motivational Boost:")
if len(this_week) >= 3:
    print("🔥 You crushed it this week! Keep this momentum going!")
elif len(this_week) > 0:
    print("🙌 Great job making progress. Let’s build on that tomorrow!")
else:
    print("💡 A little progress each day adds up. You’ve got this — just start with one lesson!")

# === Overall Progress
percent = int((len(completed) / len(all_lessons)) * 100)
print(f"\n📊 Total Progress: {percent}% complete ({len(completed)} of {len(all_lessons)} lessons)\n")
