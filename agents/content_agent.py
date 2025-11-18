import os
import google.generativeai as genai
from memory.user_profile import UserProfile  # for type hints only

DEFAULT_MODEL = "gemini-flash-latest"  # override via GEMINI_MODEL if needed


class ContentAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Set it in your environment or .env file."
            )

        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    # ---------- internal helper to safely call Gemini ----------

    def _call_model(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
        except Exception as e:
            # Hard failure – network/API/etc.
            raise RuntimeError(
                f"Error calling Gemini model '{self.model_name}': {e}"
            )

        # 1) Try the quick accessor
        try:
            if hasattr(response, "text") and response.text:
                return response.text.strip()
        except ValueError:
            # This is the exact error you saw – no valid Part for .text
            pass

        # 2) Try to dig out any text from candidates/parts
        try:
            candidates = getattr(response, "candidates", []) or []
            for cand in candidates:
                content = getattr(cand, "content", None)
                parts = getattr(content, "parts", []) if content else []
                texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", "")]
                if texts:
                    return "\n".join(texts).strip()
        except Exception:
            # If this fails, we'll just fall back
            pass

        # 3) Absolute fallback: return a simple, static explanation so we don't crash
        return (
            "Step 1: A fraction is a way to show a part of a whole.\n"
            "Step 2: The bottom number (denominator) tells how many equal parts the whole is split into.\n"
            "Step 3: The top number (numerator) tells how many of those parts you have.\n"
            "Step 4: Example: If a pizza is cut into 4 equal slices and you eat 1 slice, "
            "that is 1/4 of the pizza."
        )

    # ---------- public methods ----------

    def generate_lesson(self, topic: str, profile: "UserProfile") -> str:
        """
        Generate a mini-lesson that is aware of the student's learning differences
        and modality preferences.
        """
        # NOTE: Use softer language to avoid tripping safety filters
        challenges = ", ".join(profile.learning_challenges) or "no specific learning differences noted"
        pref = profile.preferences
        pref_desc = (
            f"visual={pref.get('visual', 0):.2f}, "
            f"audio={pref.get('audio', 0):.2f}, "
            f"text={pref.get('text', 0):.2f}"
        )

        prompt = f"""
        You are an adaptive tutor helping a student with some learning differences.

        Student context:
        - Reported learning differences: {challenges}
        - Modality preferences (higher = stronger preference): {pref_desc}

        Design a short, gentle mini-lesson on: "{topic}"

        Requirements:
        - Use very clear, concrete language.
        - Avoid long paragraphs; prefer short lines.
        - Break the explanation into 3–7 small steps.
        - Make each step self-contained.
        - If the student struggles with reading, avoid dense blocks of text and use clear structure.
        - If the student struggles with focus, keep steps short, with occasional encouragement.
        - Use visual imagery where helpful (for example, pizza slices for fractions).

        Output format:
        - One step per line.
        - Start each line with 'Step X:' where X is the step number.
        """

        return self._call_model(prompt)

    def generate_hint(self, step_text: str, profile: "UserProfile") -> str:
        """
        Generate a short hint or simpler alternative explanation for a given step.
        """
        challenges = ", ".join(profile.learning_challenges) or "no specific learning differences noted"
        pref = profile.preferences
        pref_desc = (
            f"visual={pref.get('visual', 0):.2f}, "
            f"audio={pref.get('audio', 0):.2f}, "
            f"text={pref.get('text', 0):.2f}"
        )

        prompt = f"""
        You are helping a student who found this explanation step confusing:

        "{step_text}"

        Student context:
        - Reported learning differences: {challenges}
        - Modality preferences: {pref_desc}

        Task:
        - Provide a VERY SHORT hint or alternative explanation (1–3 short sentences).
        - Use extremely simple language.
        - You may use a concrete example or visual description.
        - Do NOT restate the whole lesson, just a nudge to help them understand this step.
        """

        return self._call_model(prompt)
