class InsightAgent:
    def generate_report(self, profile, session_summary):
        total = len(session_summary)
        correct = sum(1 for log in session_summary if log["feedback"] == "correct")
        accuracy = (correct / total) * 100 if total > 0 else 0.0

        hint_count = sum(1 for log in session_summary if log.get("hint_used"))
        hint_rate = (hint_count / total) * 100 if total > 0 else 0.0

        incorrect_steps = [log for log in session_summary if log["feedback"] != "correct"]
        hardest_snippet = incorrect_steps[0]["content"][:200] if incorrect_steps else None

        lines = []
        lines.append(f"Report for {profile.name} (ID: {profile.student_id})")
        lines.append("-" * 60)
        lines.append("Session Overview")
        lines.append(f"- Learning challenges: {', '.join(profile.learning_challenges) or 'None reported'}")
        lines.append(f"- Modality preferences: {profile.preferences}")
        lines.append(f"- Steps marked understood: {correct}/{total} ({accuracy:.1f}%)")
        lines.append(f"- Steps where a hint was used: {hint_count}/{total} ({hint_rate:.1f}%)")
        lines.append("")

        # Strengths
        lines.append("Strengths")
        if accuracy >= 80:
            lines.append(
                f"- {profile.name} understood most of the steps. The current explanation style seems effective."
            )
        else:
            lines.append(
                f"- {profile.name} stayed engaged even when some steps were difficult. This persistence is a strength."
            )

        if profile.preferences.get("visual", 0) >= 0.5:
            lines.append("- Visual explanations (diagrams, imagery) are likely especially helpful.")
        if profile.preferences.get("audio", 0) >= 0.5:
            lines.append("- Hearing explanations aloud or via read-aloud tools may further support understanding.")

        lines.append("")

        # Challenges
        lines.append("Challenges Observed")
        if hardest_snippet:
            lines.append(
                "- At least one step was marked as difficult. "
                "Here is an example of a challenging step:\n"
                f'  "{hardest_snippet}..."'
            )
        else:
            lines.append("- No specific steps were marked as difficult in this session.")
        lines.append("")

        # Suggestions
        lines.append("Suggestions for Parents / Teachers")
        challenges_lower = [c.lower() for c in profile.learning_challenges]
        if "dyslexia" in challenges_lower:
            lines.append(
                "- Continue using short, well-spaced text with clear structure. "
                "Pair reading with visuals such as fraction circles or number lines."
            )
        if "adhd" in challenges_lower:
            lines.append(
                "- Short learning blocks with frequent micro-breaks are likely helpful. "
                "Consider 10–15 minute focused sessions with movement breaks in between."
            )
        if "autism" in challenges_lower:
            lines.append(
                "- Keep explanations precise and consistent. Avoid ambiguous phrasing and sudden changes in routine."
            )
        if not challenges_lower:
            lines.append(
                "- Reinforce the key ideas from this session with a quick review later in the day."
            )

        lines.append(
            "- Ask the learner to explain the concept back in their own words; this often reveals their depth of understanding."
        )
        lines.append("")

        lines.append("Session Step Log")
        for log in session_summary:
            hint_tag = " (hint used)" if log.get("hint_used") else ""
            lines.append(f"- Step {log['step_id']}: {log['feedback']}{hint_tag}")

        return "\n".join(lines)
