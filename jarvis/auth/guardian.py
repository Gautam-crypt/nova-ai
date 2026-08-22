"""
jarvis/auth/guardian.py
The single auth gate — called from main.py.
Both eye + voice must pass. One failure = shutdown.
"""

import sys
import time
import getpass # For secure password entry
from jarvis.core.senses.vision.eye_auth import verify_eye
from jarvis.auth.config import MASTER_PASSWORD

# ── Optional: import voice auth when ready ──────────────────
# from jarvis.auth.voice_enrollment import verify_voice
# ────────────────────────────────────────────────────────────

MAX_EYE_RETRIES = 2

def run_auth_gate(speak_fn=None) -> bool:
    """
    Full biometric gate.
    speak_fn: optional TTS callable, e.g. speak_fn("text")
    Returns True if owner verified, False if any check fails.
    """
    def say(text: str):
        print(f"[JARVIS] {text}")
        if speak_fn:
            speak_fn(text)

    print("\n" + "=" * 52)
    print("  J.A.R.V.I.S  —  IDENTITY VERIFICATION")
    print("=" * 52)

    say("Initiating biometric verification. Please look at the camera.")
    time.sleep(1.0)

    # ── GATE 1: Eye Recognition ──────────────────────────────
    for attempt in range(1, MAX_EYE_RETRIES + 1):
        if attempt > 1:
            say(f"Retry {attempt} of {MAX_EYE_RETRIES}. Please look directly at the camera.")
            time.sleep(1.5)

        success, confidence = verify_eye(show_window=True)
        
        if success == "PASSWORD_MODE":
            # Switch to password mode
            if _password_gate(say):
                return True
            else:
                return False

        if success:
            # Identity verified by Eye
            # (Greeting will be handled by Brain in main.py)
            print(f"[AUTH] Eye match confidence: {confidence:.2%}\n")
            break
    else:
        # If eye recognition failed, offer one last password attempt
        say("Identity not recognized. Attempting secondary authentication...")
        if _password_gate(say):
            return True
            
        say("Identity not recognized. Access denied.")
        print("[AUTH] SHUTDOWN — verification failed.")
        _lock_down()
        return False

    # ── GATE 2: Voice (uncomment when voice_enrollment ready) ─
    # say("Voice verification. Please say your passphrase.")
    # if not verify_voice():
    #     say("Voice not recognized. Access denied.")
    #     _lock_down()
    #     return False
    # say("Voice confirmed.")

    say("All gates passed. JARVIS online.\n")
    return True

def _password_gate(say_fn) -> bool:
    """Manual password entry gate."""
    say_fn("Please enter the master password.")
    
    # Flush the keyboard buffer to avoid ghost inputs from eye_auth
    if sys.platform == "win32":
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
            
    pwd = input("[SECURITY] Master Password: ").strip()
    
    if pwd == MASTER_PASSWORD:
        say_fn("Access granted by override.")
        return True
    else:
        say_fn("Incorrect password.")
        return False

def _lock_down():
    """Called on failed auth — wipe in-memory state and exit."""
    print("[SECURITY] Lockdown initiated.")
    time.sleep(0.5)
    sys.exit(1)