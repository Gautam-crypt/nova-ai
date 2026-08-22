"""
jarvis/core/senses/voice/listener.py
Improved Voice Listener using Faster-Whisper for accuracy and Vosk for robust wake-word detection.
Designed to work flawlessly on Windows with Python 3.13.
"""

import os
import time
import logging
import numpy as np
import speech_recognition as sr
import json
import queue
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()
SARVAM_STT_KEY = os.getenv("SARVAM_STT_KEY")

# --- SUPPRESS LOG NOISE ---
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# --------------------------

from faster_whisper import WhisperModel
import vosk
import pyaudio
import threading

# Configure Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("JarvisListener")

class JarvisListener:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Initializes the speech recognition and wake word models.
        """
        logger.info(f"Initializing Whisper ({model_size}) for accuracy...")
        # Mute the noisy HTTP logs
        logging.getLogger("faster_whisper").setLevel(logging.ERROR)
        
        try:
            self.stt_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception:
            print("[JARVIS] Initializing high-accuracy voice engine... please wait.")
            self.stt_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        logger.info("Initializing Vosk for robust wake-word detection...")
        # Vosk is used for the 'trigger' because it's extremely stable on Windows 3.13
        try:
            # This will download a small model if not present (approx 40MB)
            self.vosk_model = vosk.Model(lang="en-us")
            self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
        except Exception as e:
            logger.error(f"Vosk initialization failed: {e}")
            self.vosk_model = None

        self.recognizer = sr.Recognizer()
        self.mic_index = None
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def list_microphones(self):
        """Returns a list of available microphone names."""
        mics = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mics):
            print(f"[{i}]: {name}")
        return mics

    def set_microphone(self, index):
        """Sets the active microphone by index."""
        self.mic_index = index
        logger.info(f"Microphone set to index {index}")

    def calibrate(self, duration=2):
        """Calibrates for ambient noise."""
        with sr.Microphone(device_index=self.mic_index, sample_rate=16000) as source:
            logger.info(f"Calibrating for {duration}s ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            logger.info(f"Calibration complete. Threshold: {self.recognizer.energy_threshold}")

    def listen_for_command(self) -> str:
        """
        Captures audio and transcribes it using Faster-Whisper.
        """
        with sr.Microphone(device_index=self.mic_index, sample_rate=16000) as source:
            logger.info("Listening for command...")
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                audio_data = np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0
                
                # Try Sarvam STT first for better Hinglish recognition
                if SARVAM_STT_KEY:
                    try:
                        # Save temp wav for API
                        temp_wav = "data/audio/temp_input.wav"
                        os.makedirs(os.path.dirname(temp_wav), exist_ok=True)
                        with open(temp_wav, "wb") as f:
                            f.write(audio.get_wav_data())
                            
                        url = "https://api.sarvam.ai/speech-to-text"
                        headers = {"api-subscription-key": SARVAM_STT_KEY}
                        files = {'file': ('audio.wav', open(temp_wav, 'rb'), 'audio/wav')}
                        # Add model parameter for saaras:v3
                        data = {"model": "saaras:v3"}
                        
                        # Use httpx for the request
                        with httpx.Client() as client:
                            response = client.post(url, files=files, data=data, headers=headers, timeout=10.0)
                            if response.status_code == 200:
                                text = response.json().get("transcript", "").strip().lower()
                                if text:
                                    logger.info(f"Heard (Sarvam): '{text}'")
                                    return text
                    except Exception as e:
                        logger.error(f"Sarvam STT Error: {e}. Falling back to Whisper.")

                # Fallback to local Faster-Whisper
                segments, info = self.stt_model.transcribe(audio_data, beam_size=5)
                text = " ".join([segment.text for segment in segments]).strip().lower()
                
                if text:
                    logger.info(f"Heard (Whisper): '{text}'")
                    return text
                    
            except sr.WaitTimeoutError:
                logger.warning("Listening timed out.")
            except Exception as e:
                logger.error(f"Error during listening: {e}")
                
        return ""

    def listen_for_wake_word_streaming(self):
        """
        Robust streaming wake word detection using Vosk.
        Extremely reliable on Windows and low resource usage.
        """
        if not self.vosk_model:
            logger.error("Vosk model not available. Falling back to Whisper-only mode.")
            return True # Fallback to continue

        CHUNK = 4000
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        audio = pyaudio.PyAudio()
        try:
            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                               input=True, frames_per_buffer=CHUNK,
                               input_device_index=self.mic_index)
        except Exception as e:
            logger.error(f"Could not open microphone stream: {e}")
            return False

        logger.info("Listening for 'Hello' (Robust Mode)...")
        
        import msvcrt
        try:
            while True:
                # Check for keyboard interrupt
                if msvcrt.kbhit():
                    return False # Return False to indicate keyboard interruption
                
                data = stream.read(CHUNK, exception_on_overflow=False)
                if self.vosk_rec.AcceptWaveform(data):
                    res = json.loads(self.vosk_rec.Result())
                    text = res.get("text", "").lower()
                    if "hello" in text:
                        logger.info("Wake word DETECTED!")
                        return True
                else:
                    # Partial results for faster feel
                    partial = json.loads(self.vosk_rec.PartialResult())
                    if "hello" in partial.get("partial", "").lower():
                        logger.info("Wake word DETECTED (partial)!")
                        return True
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            return False
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

# Global instance for easy import/usage
_listener = None

def get_listener():
    global _listener
    if _listener is None:
        _listener = JarvisListener()
    return _listener

def listen(timeout=5) -> str:
    """Wrapper function to match previous API."""
    ls = get_listener()
    if ls.mic_index is None:
        ls.set_microphone(None)
        ls.calibrate()
    return ls.listen_for_command()

def check_for_wake_word(text: str, wake_word="hello") -> tuple[bool, str]:
    """Improved wake word check."""
    text = text.lower().strip()
    if wake_word in text:
        cleaned = text.replace(wake_word, "").strip().lstrip(".,! ")
        return True, cleaned
    return False, text
