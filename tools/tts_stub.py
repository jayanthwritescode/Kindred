"""
Tool: TTS Stub

Simulates text-to-speech behavior. In a real system, this would call
an actual TTS API and return an audio file or URL. Here we just return
a string marker so the tutor can show where audio would be played.
"""

def tts_stub(text: str) -> str:
    """
    Return a placeholder "audio" description for the given text.
    """
    short = text.strip().split("\n")[0]
    if len(short) > 120:
        short = short[:117] + "..."
    return f"[TTS] Would read aloud: \"{short}\""

