class UserProfile:
    def __init__(self, student_id, name, preferences, learning_challenges=None, notes=""):
        self.student_id = student_id
        self.name = name
        self.preferences = preferences
        self.learning_challenges = learning_challenges or []
        self.notes = notes

    def update_preferences(self, feedback):
        for mode, delta in feedback.items():
            self.preferences[mode] = max(0.0, min(1.0, self.preferences.get(mode, 0) + delta))
        total = sum(self.preferences.values())
        for mode in self.preferences:
            self.preferences[mode] /= total

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "preferences": self.preferences,
            "learning_challenges": self.learning_challenges,
            "notes": self.notes
        }

    def __str__(self):
        return f"UserProfile({self.student_id}, Preferences={self.preferences})"
