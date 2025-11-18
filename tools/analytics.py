"""
Tool: Analytics

Provides reusable functions to analyze session logs and compute
scores for updating the student profile.
"""

def compute_effective_score(session_summary: list[dict]) -> float:
    """
    Compute an 'effective score' based on correctness and hint usage.

    - Base score = raw accuracy (correct / total).
    - Using hints reduces effective score slightly, since it indicates
      the student needed extra support.

    Returns a value between 0 and 1.
    """
    total = len(session_summary)
    if total == 0:
        return 0.0

    correct = sum(1 for log in session_summary if log["feedback"] == "correct")
    hints_used = sum(1 for log in session_summary if log.get("hint_used"))

    accuracy = correct / total
    hint_rate = hints_used / total

    # Penalize heavy hint usage a bit
    effective = max(0.0, accuracy - 0.3 * hint_rate)
    return effective

