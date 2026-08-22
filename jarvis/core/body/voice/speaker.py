"""
jarvis/core/body/voice/speaker.py
Vocal Emotion Sync for NOVA (formerly JARVIS). 
Updates voice to female and adjusts rate/pitch based on emotion.
"""

import os
import asyncio
import edge_tts
import pygame
import httpx
import base64
import pyttsx3
from dotenv import load_dotenv
from jarvis.api.bridge import send_event
import re

def clean_for_tts(text: str) -> str:
    # Remove all emojis
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F9FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # Remove (Emotion: xyz) tags
    text = re.sub(r'\(Emotion:.*?\)', '', text)
    
    # Remove action tags like *smiles* or [DIVYA]
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\*.*?\*', '', text)
    
    # Fix common issues
    text = text.replace('  ', ' ').strip()
    
    return text

load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_TTS_KEY")

# Female Voices: en-US-EmmaNeural, en-GB-SoniaNeural, en-US-AvaNeural
VOICE = "en-US-EmmaNeural" 
OUTPUT_FILE = "data/audio/speech.mp3"

# Map emotions to Edge-TTS voice styling
EMOTION_STYLING = {
    "tired": {"rate": "-25%", "pitch": "-5Hz"},
    "sad": {"rate": "-15%", "pitch": "-3Hz"},
    "stressed": {"rate": "-10%", "pitch": "+0Hz"},
    "happy": {"rate": "+15%", "pitch": "+5Hz"},
    "casual": {"rate": "+5%", "pitch": "+0Hz"},
    "neutral": {"rate": "+0%", "pitch": "+0Hz"},
    "very_stressed": {"rate": "-5%", "pitch": "+2Hz"},
    "angry": {"rate": "+10%", "pitch": "+0Hz"}
}

def speak(text: str, emotion: str = "neutral"):
    """Speaks the text aloud with emotional styling."""
    if not text:
        return
        
    print(f"[NOVA]: {text} (Emotion: {emotion})")
    send_event("SPEECH_START", {"text": text})
    
    clean_text = clean_for_tts(text)
    
    try:
        # Run the async function in a clean loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_generate_and_play(clean_text, emotion))
        loop.close()
    except Exception as e:
        print(f"[SPEAKER ERROR]: {e}")
    finally:
        send_event("SPEECH_END", {})

async def _generate_and_play(text: str, emotion: str):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    import re
    # Check if text contains Devanagari characters
    is_hindi = bool(re.search(r'[\u0900-\u097F]', text))
    
    # 1. Try Sarvam TTS first for Hindi text
    if is_hindi and SARVAM_API_KEY:
        try:
            url = "https://api.sarvam.ai/text-to-speech"
            headers = {
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": [text],
                "target_language_code": "hi-IN", 
                "speaker": "anushka",
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.5,
                "speech_sample_rate": 24000
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    audio_content = response.json().get("audio_content")
                    if audio_content:
                        with open(OUTPUT_FILE, "wb") as f:
                            f.write(base64.b64decode(audio_content))
                        
                        _play_audio()
                        return
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[SARVAM TTS ERROR]: {e}. Falling back to Edge-TTS.")

    # 2. Try Edge-TTS
    try:
        import edge_tts
        VOICE = "hi-IN-SwaraNeural" if is_hindi else "en-IN-NeerjaNeural"
        style = EMOTION_STYLING.get(emotion, EMOTION_STYLING["neutral"])
        communicate = edge_tts.Communicate(text, VOICE, rate=style["rate"], pitch=style["pitch"])
        await communicate.save(OUTPUT_FILE)
        _play_audio()
        return
    except Exception as e:
        print(f"[EDGE-TTS ERROR]: {e}. Using offline Pyttsx3.")
        _play_pyttsx3(text)

def _play_pyttsx3(text: str):
    """Offline fallback using system voices."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # Try to find a female voice
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 180)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[PYTTSX3 ERROR]: {e}")

def _play_audio():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT_FILE)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
