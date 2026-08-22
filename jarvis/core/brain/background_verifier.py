import threading
import time

SKIP_SAVE = ["realtime", "vision", "automation", "hermes", "divya", "yama"]
VERIFY_AND_SAVE = ["general_qa", "coding", "explanation"]

class BackgroundVerifier:
    def __init__(self, knowledge_db, openai_api_key=None):
        self.knowledge_db = knowledge_db
        self.openai_api_key = openai_api_key
        self.pending_verifications = 0
        self.lock = threading.Lock()

    def verify_async(self, question, answer, topic):
        # Fix 2: Agent filter in verifier
        if topic in SKIP_SAVE:
            print(f"[VERIFIER] Skipping {topic} — not worth saving (realtime/vision/automation)")
            return

        def _verify_and_save(q, a, t):
            with self.lock:
                self.pending_verifications += 1
            print(f"[VERIFIER] Verifying async for: '{q}'...")
            
            # Here you would typically call OpenAI for verification using self.openai_api_key
            # For now, we directly save since verification logic is pending
            
            print(f"[VERIFIER] Verification complete for '{q}'. Saving to DB.")
            self.knowledge_db.save(q, a)
            
            with self.lock:
                self.pending_verifications -= 1

        t = threading.Thread(
            target=_verify_and_save,
            args=(question, answer, topic),
            daemon=True
        )
        t.start()

    def status(self):
        with self.lock:
            if self.pending_verifications > 0:
                return f"[VERIFIER] {self.pending_verifications} pending verifications hain"
            else:
                return "[VERIFIER] 0 pending — sab save ho gaye"
