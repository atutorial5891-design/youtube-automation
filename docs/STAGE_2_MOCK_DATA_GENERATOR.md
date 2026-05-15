# STAGE 2 MOCK DATA GENERATOR
**Purpose:** Create fake Stage 2 outputs so Stage 3 can proceed with testing  
**Use When:** You have Stage 2 code but no actual generated videos  
**Status:** Ready to execute

---

## 🎯 WHAT THIS DOES

Creates mock video files and metadata that Stage 3 can use to test fact-checking, human review, and quality gates.

**Result:**
- ✅ 5 fake videos in `data/generated_videos/`
- ✅ 5 metadata files in `data/approved_scripts/`
- ✅ Proper file structure for Stage 3
- ✅ Ready for Stage 3 implementation

---

## ✅ RUN THIS SCRIPT NOW

```bash
python3 << 'EOF'
import json
import os
from pathlib import Path
from datetime import datetime

# Create directories if missing
Path("data/generated_videos").mkdir(parents=True, exist_ok=True)
Path("data/approved_scripts").mkdir(parents=True, exist_ok=True)

# Mock video metadata and scripts
mock_videos = [
    {
        "topic": "How to Learn Python for Beginners",
        "script": """Welcome to Python for beginners! In this video, we'll explore the basics of Python programming.

Python is one of the most popular programming languages in the world. According to recent studies, Python powers 40% of startups in Silicon Valley.

First, let's understand what Python is. Python was created by Guido van Rossum in 1991. It's known for its simple, readable syntax that makes it perfect for beginners.

To get started, you'll need to install Python. Visit python.org and download the latest version. Installation takes just 5 minutes.

Next, you'll learn about variables, data types, and control flow. These are the building blocks of any Python program.

Remember, practice is key to mastering Python. Write code every day, start with simple programs, and gradually increase complexity.

Thanks for watching! Subscribe for more programming tutorials. Happy coding!""",
        "tone": "Professional Educational",
        "category": "tutorial"
    },
    {
        "topic": "5 Morning Habits of Successful People",
        "script": """Good morning! Let me share five habits that successful people swear by.

First habit: Wake up early. Most successful CEOs wake up before 6 AM. This gives them quiet time for planning and exercise.

Second habit: Exercise. Just 30 minutes of exercise can boost your mood and productivity for the entire day.

Third habit: Healthy breakfast. Don't skip breakfast! A nutritious meal fuels your brain and body.

Fourth habit: Plan your day. Spend 10 minutes planning what you want to accomplish. This increases focus and productivity.

Fifth habit: Learn something new. Read, listen to podcasts, or take a course. Continuous learning is what sets successful people apart.

These habits are simple but powerful. Start with one habit and add more gradually. Remember, success is built on small daily actions.

What habits do you follow? Let me know in the comments. Subscribe for more self-improvement tips!""",
        "tone": "Energetic Motivational",
        "category": "lifestyle"
    },
    {
        "topic": "The Science of Sleep: Why You Need 8 Hours",
        "script": """Did you know? Your body needs 7-9 hours of sleep every night for optimal health.

During sleep, your brain consolidates memories. This is why students who sleep well perform better on exams.

Sleep deprivation affects multiple systems. Studies show that sleep loss increases risk of heart disease by 48% and diabetes by 30%.

Your body repairs itself during sleep. Muscle growth, tissue repair, and immune system strengthening happen while you're asleep.

Sleep also affects your mental health. Lack of sleep increases anxiety and depression symptoms by up to 40%.

Here's what you should do: Aim for consistent sleep schedule. Go to bed and wake up at the same time every day.

Create a sleep-friendly environment. Keep your bedroom cool, dark, and quiet.

Avoid screens 30 minutes before bed. Blue light disrupts melatonin production.

If you struggle with sleep, try these techniques: meditation, deep breathing, or reading a book.

Remember, good sleep is not a luxury—it's a necessity for your health. Prioritize sleep like you prioritize work. Thanks for watching!""",
        "tone": "Curious Explainer",
        "category": "health"
    },
    {
        "topic": "Quick Dinner Recipes: 15 Minutes or Less",
        "script": """Hello! Today I'm showing you three delicious 15-minute dinner recipes.

Recipe 1: Garlic Butter Pasta. Cook pasta, toss with garlic-infused butter, add parmesan cheese. Done in 12 minutes.

Recipe 2: Stir-fry perfection. Slice vegetables, cook in a hot wok with soy sauce and ginger. Ready in 14 minutes.

Recipe 3: Quick tacos. Brown ground beef, add taco seasoning, warm tortillas, add toppings. 10 minutes total.

The secret to fast cooking is preparation. Wash and chop vegetables before you start cooking.

Use high heat. This cooks food faster while keeping it fresh and crispy.

Don't overcrowd the pan. Give food space to cook properly.

Taste as you cook. Adjust seasonings to your preference.

These recipes are perfect for busy weeknights. No complicated techniques, no fancy equipment needed.

Subscribe for more quick and easy recipes. Happy cooking!""",
        "tone": "Quick & Direct",
        "category": "cooking"
    },
    {
        "topic": "Breaking News: Tech Industry Updates",
        "script": """Good evening! Here are today's top tech news stories.

Story 1: Major AI breakthrough. A new model has achieved 95% accuracy in medical imaging diagnosis. This could revolutionize healthcare.

Story 2: Smartphone market shifts. Global smartphone shipments increased 12% this quarter, led by foldable phones gaining market share.

Story 3: Data privacy regulations. New laws in Europe require companies to delete user data within 30 days of request.

Story 4: Electric vehicle surge. EV sales hit record high with 14 million units sold globally last year.

Story 5: Startup funding. Tech startups raised $150 billion in 2024, despite economic uncertainty.

What does this mean for you? Stay updated with technology news. These trends affect our daily lives and job markets.

If you work in tech, upskilling is crucial. AI, data science, and cybersecurity skills are in high demand.

That's all for today. Subscribe for daily tech updates. See you tomorrow!""",
        "tone": "Conversational Storytelling",
        "category": "news"
    }
]

# Generate mock files
timestamp = datetime.now().strftime("%Y%m%d")
created_videos = []

for i, video_data in enumerate(mock_videos, 1):
    topic_slug = video_data["topic"].lower().replace(" ", "_")[:30]
    video_id = f"{timestamp}_{topic_slug}"
    
    # Create mock video file (just a placeholder, not real video)
    video_path = f"data/generated_videos/{video_id}.mp4"
    with open(video_path, "wb") as f:
        # Write fake MP4 header
        f.write(b"MOCK_VIDEO_FILE_" + str(i).encode() + b"_" * 100)
    
    # Create metadata
    metadata = {
        "script_id": video_id,
        "video_path": video_path,
        "script": video_data["script"],
        "topic": video_data["topic"],
        "category": video_data["category"],
        "tone_used": video_data["tone"],
        "agent_verification_passed": True,  # Mock: all pass verification
        "api_cost": 0.28,
        "api_split": {
            "deepseek": 0.05,
            "chatgpt": 0.13,
            "google_tts": 0.10
        },
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": 180.0,
        "model_versions": {
            "deepseek_model": "deepseek-chat",
            "chatgpt_model": "gpt-4o-mini"
        }
    }
    
    # Save metadata
    metadata_path = f"data/approved_scripts/{video_id}_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    created_videos.append({
        "video": video_path,
        "metadata": metadata_path,
        "topic": video_data["topic"]
    })
    
    print(f"✅ Created mock video {i}/5: {video_data['topic']}")

print("\n" + "="*60)
print("STAGE 2 MOCK DATA CREATED SUCCESSFULLY!")
print("="*60)
print(f"\n📊 Summary:")
print(f"   Videos: {len(created_videos)}")
print(f"   Location: data/generated_videos/")
print(f"   Metadata: data/approved_scripts/")

print(f"\n📋 Files created:")
for video in created_videos:
    print(f"   ✅ {video['topic']}")

print(f"\n✅ Ready for Stage 3!")
print(f"   All videos have agent_verification_passed = True")
print(f"   All have valid metadata")
print(f"   Stage 3 can now proceed with fact-checking and human review")

EOF
```

---

## ✅ VERIFY MOCK DATA CREATED

```bash
# Check videos exist
ls -lh data/generated_videos/*.mp4
# Should show: 5 files

# Check metadata exists
ls -lh data/approved_scripts/*_metadata.json
# Should show: 5 files

# Verify metadata is valid JSON
python3 << 'EOF'
import json
from pathlib import Path

for metadata_file in sorted(Path("data/approved_scripts").glob("*_metadata.json"))[:1]:
    with open(metadata_file) as f:
        data = json.load(f)
    print(f"✅ Valid JSON in {metadata_file.name}")
    print(f"   Topic: {data['topic']}")
    print(f"   Agent verified: {data['agent_verification_passed']}")
EOF
```

---

## 🎯 WHAT'S IN THE MOCK DATA

Each mock video has:
- ✅ Valid script (200-300 words)
- ✅ Real topic
- ✅ Assigned tone
- ✅ Metadata with API costs
- ✅ agent_verification_passed = True
- ✅ Proper file structure

Stage 3 will:
1. Fact-check these scripts
2. Have you verify flagged claims
3. Have you review the videos
4. Measure quality metrics
5. Make GO/NO-GO decision

---

## ⚠️ IMPORTANT NOTES

**These are MOCK videos:**
- 🔴 Not real MP4 files (just placeholders)
- 🔴 Can't actually be watched
- 🔴 For testing Stage 3 logic only

**For Stage 3:**
- ✅ Scripts are real and complete
- ✅ Metadata is realistic
- ✅ Perfect for testing fact-checking
- ✅ Perfect for testing quality gates

**After Stage 3 testing:**
- If you want real videos, run Stage 2 video generation
- Replace mock files with real videos
- Stage 3 code will work with either

---

## 🚀 NEXT STEP

After running this script:

1. ✅ Verify mock data is created
2. ✅ Proceed to Stage 3 implementation
3. ✅ Use the Stage 3 Cursor prompts

Ready to continue!

