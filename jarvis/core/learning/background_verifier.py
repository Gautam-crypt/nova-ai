import threading
import openai
import json
from .knowledge_db import KnowledgeDB

class BackgroundVerifier:
    """
    Verification runs in daemon thread — main conversation never blocks.
    
    Flow:
    1. verify_async() called after local answer generated
    2. Daemon thread starts — user gets local answer immediately
    3. Background: OpenAI verifies + improves answer
    4. Permanently saved to KnowledgeDB
    5. Next time same question → instant DB answer, no API
    """
    
    def __init__(self, knowledge_db: KnowledgeDB, openai_api_key: str):
        self.db = knowledge_db
        # Using Groq API endpoint with the provided key
        self.client = openai.OpenAI(
            api_key=openai_api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self._pending_count = 0
        self._lock = threading.Lock()
    
    def verify_async(self, question: str, local_answer: str):
        """Non-blocking — fire and forget"""
        with self._lock:
            self._pending_count += 1
        
        t = threading.Thread(
            target=self._verify_and_save,
            args=(question, local_answer),
            daemon=True,
            name=f"verifier_{question[:20]}"
        )
        t.start()
    
    def _detect_topic(self, question: str) -> str:
        """Simple topic tagging — OpenAI call nahi, local logic"""
        q = question.lower()
        if any(w in q for w in ["code","python","function","bug","error","script"]):
            return "coding"
        elif any(w in q for w in ["weather","news","today","latest","current"]):
            return "realtime"
        elif any(w in q for w in ["kya","kyun","kaise","explain","what","how","why"]):
            return "general_qa"
        elif any(w in q for w in ["music","gana","song","play"]):
            return "entertainment"
        elif any(w in q for w in ["reminder","alarm","schedule","meeting","kal"]):
            return "scheduling"
        return "general"
    
    def _verify_and_save(self, question: str, local_answer: str):
        try:
            topic = self._detect_topic(question)
            
            prompt = f"""
You are a response quality verifier for NOVA, a Hinglish AI assistant.

Original question: "{question}"
Local AI answer: "{local_answer}"

YOUR TASKS:
1. Check if the answer is factually correct
2. Improve it if needed — more accurate and natural
3. CRITICAL: verified_answer MUST be in Hinglish (Hindi+English mix)
   - If local_answer is in pure English → convert to Hinglish
   - If local_answer is already Hinglish → keep style, just fix facts
4. Keep it SHORT — max 2 sentences
5. Dost style — casual, UP/Delhi vibe, use "yaar/bhai"

HINGLISH conversion examples:
English: "It's okay to feel that way! Try relaxing techniques."
Hinglish: "Arre yaar normal hai ye 😄 aaj jaldi so ja, fresh feel karega!"

English: "Yogi Adityanath is the Chief Minister of Uttar Pradesh."  
Hinglish: "Yogi Adityanath hai UP ka CM bhai — March 2022 se hai!"

Return ONLY valid JSON, no markdown:
{{
    "verified_answer": "Hinglish answer here",
    "quality_score": 0.85,
    "corrections_made": true,
    "topic": "{topic}"
}}
"""
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=350
            )
            
            raw  = response.choices[0].message.content.strip()
            # Handle potential markdown formatting from LLM
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
            
            data = json.loads(raw)
            
            verified = data.get("verified_answer", local_answer)
            score    = float(data.get("quality_score", 0.7))
            fixed    = bool(data.get("corrections_made", False))
            
            # Reject if verified_answer is still pure English
            english_only_check = not any(w in verified.lower() for w in [
                "yaar","bhai","hai","nahi","kar","tha","thi","hun",
                "kya","aur","toh","bata","arre","dekh","le","de"
            ])
            if english_only_check and score < 0.90:
                print(f"[VERIFIER] Rejected — pure English response, not saving to DB")
                return
            
            # Quality threshold — sirf achhe answers save karo
            if (score >= 0.65 and fixed) or (score >= 0.85 and not fixed):
                self.db.save(
                    question        = question,
                    local_answer    = local_answer,
                    verified_answer = verified,
                    quality_score   = score,
                    corrections_made= fixed,
                    source          = "openai_verified",
                    topic_tag       = topic
                )
                print(f"\n[VERIFIER] [OK] Saved to DB — topic: {topic}, score: {score:.2f}, fixed: {fixed}")
            else:
                print(f"\n[VERIFIER] [X] Skipping — uncertain quality (score: {score:.2f}, fixed: {fixed})")
        
        except json.JSONDecodeError as e:
            print(f"\n[VERIFIER] JSON parse error: {e} - Raw: {raw}")
        except Exception as e:
            print(f"\n[VERIFIER] Error: {e}")
        finally:
            with self._lock:
                self._pending_count -= 1
    
    def pending_count(self) -> int:
        with self._lock:
            return self._pending_count
