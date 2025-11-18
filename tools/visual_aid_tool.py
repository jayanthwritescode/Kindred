"""
Tool: Visual Aid Generator

Provides simple text-based visual descriptions to help
visual / dyslexic learners imagine the concept.
"""

def generate_visual_aid_description(topic: str, step_text: str) -> str:
    """
    Given the current topic and step text, return a short
    visual description that could be drawn or imagined.
    """
    topic_lower = topic.lower()
    if "fraction" in topic_lower:
        return (
            "Visual idea: Imagine a pizza cut into equal slices. "
            "Shade the slices that the fraction is talking about."
        )
    if "number line" in step_text.lower():
        return (
            "Visual idea: Draw a straight line, mark 0 at the left, 1 at the right, "
            "and place evenly spaced tick marks in between."
        )

    # Generic fallback
    return (
        "Visual idea: Draw a simple picture or diagram that shows this idea. "
        "Labels should be large and clear, with plenty of space between words."
    )

