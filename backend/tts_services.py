from gtts import gTTS
import io
import os
from datetime import datetime

def generate_tts_audio(text: str, save_dir: str = "tts_output"):
    """
    Generate speech from text.
    Returns: BytesIO (in-memory MP3)
    Also saves a local copy in `save_dir/tts_<timestamp>.mp3`
    """
    if not text:
        raise ValueError("No text provided for TTS generation.")

    # Ensure save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Generate speech
    tts = gTTS(text)
    mp3_bytes = io.BytesIO()
    tts.write_to_fp(mp3_bytes)
    mp3_bytes.seek(0)

    # Create timestamped filename
    filename = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    file_path = os.path.join(save_dir, filename)

    # Save to disk
    with open(file_path, "wb") as f:
        f.write(mp3_bytes.getvalue())

    print(f"[TTS] Saved local file: {file_path}")

    # Return both
    return mp3_bytes, file_path
