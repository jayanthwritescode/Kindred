import argparse
from agents.tutor_agent import TutorAgent
from agents.content_agent import ContentAgent
from agents.insight_agent import InsightAgent
from memory.user_profile import UserProfile
from memory.session_memory import SessionMemory
from tools.analytics import compute_effective_score
import json
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Run EduBridge tutoring session")
    parser.add_argument("--student", type=str, default="student_001", help="Student ID")
    parser.add_argument("--name", type=str, default="Alex", help="Student Name")
    parser.add_argument("--topic", type=str, default="Introduction to Fractions", help="Learning Topic")
    parser.add_argument("--profile", type=str, help="Path to student profile JSON")
    args = parser.parse_args()

    # Load or create profile
    if args.profile and os.path.exists(args.profile):
        with open(args.profile, "r") as f:
            data = json.load(f)
        profile = UserProfile(**data)
    else:
        profile = UserProfile(
            student_id=args.student,
            name=args.name,
            preferences={"visual": 0.6, "audio": 0.3, "text": 0.1},
            learning_challenges=["dyslexia"],
            notes="Prefers short explanations and visual aids",
        )

    session_memory = SessionMemory()
    content_agent = ContentAgent()
    tutor_agent = TutorAgent(
        content_agent=content_agent,
        session_memory=session_memory,
        profile=profile,
    )
    insight_agent = InsightAgent()

    topic = args.topic
    session_summary = tutor_agent.run_session(topic)

    # TOOL: analytics computes effective score
    effective_score = compute_effective_score(session_summary)

    # Use effective score + challenges to adjust preferences
    feedback_delta = {"visual": 0.0, "audio": 0.0, "text": 0.0}
    challenges_lower = [c.lower() for c in profile.learning_challenges]

    if effective_score >= 0.8:
        # Current style worked; reward dominant preference slightly
        dominant = max(profile.preferences, key=profile.preferences.get)
        feedback_delta[dominant] += 0.05
    else:
        # Struggled: for dyslexia/ADHD, more visual, less text
        if "dyslexia" in challenges_lower or "adhd" in challenges_lower:
            feedback_delta["visual"] += 0.05
            feedback_delta["text"] -= 0.05
        else:
            feedback_delta["audio"] += 0.03
            feedback_delta["visual"] += 0.02
            feedback_delta["text"] -= 0.05

    profile.update_preferences(feedback_delta)

    # Generate and print report
    report = insight_agent.generate_report(profile, session_summary)
    print("\n===== SESSION REPORT =====\n")
    print(report)

    # Save report + updated profile
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{profile.student_id}_report.json", "w") as f:
        json.dump(session_summary, f, indent=2)
    with open(f"reports/{profile.student_id}_profile.json", "w") as f:
        json.dump(profile.to_dict(), f, indent=2)


if __name__ == "__main__":
    main()
