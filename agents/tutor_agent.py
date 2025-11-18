from tools.break_scheduler import should_take_break
from tools.visual_aid_tool import generate_visual_aid_description
from tools.tts_stub import tts_stub


class TutorAgent:
    def __init__(self, content_agent, session_memory, profile):
        self.content_agent = content_agent
        self.session_memory = session_memory
        self.profile = profile

    def _interpret_feedback(self, raw: str, default_positive: bool = False) -> str:
        """
        Map free-form input to 'correct' or 'incorrect'.
        default_positive: if True, empty input is treated as positive.
        """
        if raw is None:
            raw = ""
        normalized = raw.lower().strip()

        if normalized == "" and default_positive:
            return "correct"

        positive_responses = {
            "correct", "c", "yes", "y", "understood", "ok", "okay", "true", "got it"
        }
        negative_responses = {
            "incorrect", "i", "no", "n", "confused", "idk", "don't know", "false"
        }

        if normalized in positive_responses:
            return "correct"
        elif normalized in negative_responses:
            return "incorrect"
        else:
            # Unknown → treat as incorrect
            return "incorrect"

    def run_session(self, topic: str):
        print(f"\nHello {self.profile.name}! Today we'll learn about: {topic}\n")

        # Agent calls ContentAgent (which itself uses Gemini) — LLM tool
        lesson = self.content_agent.generate_lesson(topic, self.profile)
        steps = [s for s in lesson.split("\n") if s.strip()]

        incorrect_streak = 0
        last_break_step = None
        has_adhd = any(ch.lower() == "adhd" for ch in self.profile.learning_challenges)

        for i, step in enumerate(steps):
            print(f"Step {i+1}: {step}")

            # TOOL: visual aid suggestion for strong visual preference
            if self.profile.preferences.get("visual", 0) >= 0.5:
                visual_hint = generate_visual_aid_description(topic, step)
                print("Visual support:", visual_hint)

            # TOOL: TTS stub for strong audio preference
            if self.profile.preferences.get("audio", 0) >= 0.5:
                audio_marker = tts_stub(step)
                print(audio_marker)

            # First pass: understanding check (Enter = yes by default)
            raw = input(
                "Did you understand this step? "
                "(Enter = yes, or type no/incorrect if not): "
            )
            interpreted = self._interpret_feedback(raw, default_positive=True)

            hint_used = False

            if interpreted == "correct":
                feedback = "correct"
                incorrect_streak = 0
                print("Awesome! 👍 Let's keep going.\n")
            else:
                # Offer a hint
                print("Thanks for letting me know. That's totally okay! 💡")
                want_hint_raw = input(
                    "Would you like a short hint or simpler explanation? "
                    "(Enter = yes, type no if you want to skip): "
                )
                want_hint = self._interpret_feedback(want_hint_raw, default_positive=True)

                if want_hint == "correct":  # i.e., yes
                    hint_used = True
                    # TOOL: hint generator inside ContentAgent
                    hint = self.content_agent.generate_hint(step, self.profile)
                    print("\nHere’s a hint:\n", hint, "\n")

                    # Second check after hint (Enter = yes)
                    raw2 = input(
                        "Does this hint help you understand the step now? "
                        "(Enter = yes, type no if still confused): "
                    )
                    interpreted2 = self._interpret_feedback(raw2, default_positive=True)

                    if interpreted2 == "correct":
                        feedback = "correct"
                        incorrect_streak = 0
                        print("Great, happy that helped! 🌟\n")
                    else:
                        feedback = "incorrect"
                        incorrect_streak += 1
                        print("No problem, we can revisit this in a future session. 🧩\n")
                else:
                    # Student declined a hint
                    feedback = "incorrect"
                    incorrect_streak += 1
                    print("Okay, we’ll move on for now and can come back later. 🧩\n")

            # Log interaction with raw + hint flag
            self.session_memory.log_interaction(
                step_id=i + 1,
                content=step,
                feedback=feedback,
                raw_feedback=raw or "<enter>",
                hint_used=hint_used,
            )

            # TOOL: break scheduler decides if we should propose a micro-break
            if should_take_break(
                has_adhd=has_adhd,
                step_index=i,
                incorrect_streak=incorrect_streak,
                last_break_step=last_break_step,
            ):
                print("Quick focus break! 🧘‍♂️")
                print("Stand up, stretch, look away from the screen for a few seconds.")
                input("Press Enter when you're ready to continue...\n")
                last_break_step = i

        return self.session_memory.get_summary()
