"""
Tool: Break Scheduler

Decides when to suggest a micro-break to support focus,
especially for learners with ADHD.
"""

def should_take_break(
    has_adhd: bool,
    step_index: int,
    incorrect_streak: int,
    last_break_step: int | None,
) -> bool:
    """
    Returns True if we should suggest a break.

    Heuristics:
    - Only active if has_adhd is True.
    - If incorrect_streak >= 2 -> suggest break.
    - Otherwise, at most every 3 steps, and not on the very first step.
    """
    if not has_adhd:
        return False

    if incorrect_streak >= 2:
        return True

    if step_index == 0:
        return False

    if last_break_step is None:
        # First break after 3 steps
        return (step_index + 1) % 3 == 0

    # Avoid breaks too close together
    steps_since_break = step_index - last_break_step
    if steps_since_break >= 3:
        return True

    return False

