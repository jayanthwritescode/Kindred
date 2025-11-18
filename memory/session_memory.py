class SessionMemory:
    def __init__(self):
        self.logs = []

    def log_interaction(self, step_id, content, feedback, raw_feedback, hint_used):
        """
        feedback: "correct" / "incorrect"
        raw_feedback: what the user actually typed (or "<enter>" if empty)
        hint_used: bool – whether a hint was shown for this step
        """
        self.logs.append({
            "step_id": step_id,
            "content": content,
            "feedback": feedback,
            "raw_feedback": raw_feedback,
            "hint_used": hint_used,
        })

    def get_summary(self):
        return self.logs
