from jarvis.core.agent_base import BaseAgent, AgentResult
from typing import Dict, Any
import chromadb
from jarvis.core.background.findings_queue import Finding, Priority, ActionType

EMOTION_KEYWORDS = {
    "stressed": [
        "stressed","tension","problem","stuck","nahi chal raha",
        "frustrated","pareshan","mushkil","deadline","help","error",
        "kaam nahi","toot gaya","thak gaya","overwhelmed"
    ],
    "happy": [
        "happy","mast","badhiya","khush","amazing","great","acha",
        "sahi","ekdum","party","yay","haha","lol","😄","perfect"
    ],
    "tired": [
        "tired","thaka","neend","so ja","raat","late","uthna",
        "exhausted","bore","bored","aadat","kal raat","sogya"
    ],
    "sad": [
        "sad","dukhi","akela","lonely","miss","cry","ro","bura",
        "feel nahi","down","depressed","hurt","pain"
    ],
    "excited": [
        "excited","wow","kya baat","seriously","no way","yaar sach",
        "believe nahi","zabardast","dhamaal","fire","🔥"
    ]
}

def detect_emotion(text: str) -> str:
    text_lower = text.lower()
    scores = {emotion: 0 for emotion in EMOTION_KEYWORDS}
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[emotion] += 1
    
    max_emotion = max(scores, key=scores.get)
    
    if scores[max_emotion] == 0:
        return "neutral"
    
    return max_emotion

class ManasAgent(BaseAgent):
    def __init__(self):
        super().__init__("manas")
        self.keywords = ["feel", "sad", "happy", "stressed", "anxious", "bored", "lonely", "tired", "thak", "pareshan", "dukhi", "khush"]

    def can_handle(self, task: Dict[str, Any]) -> bool:
        query = task.get("query", task.get("task", "")).lower()
        return any(k in query for k in self.keywords)

    def execute(self, task: dict) -> AgentResult:
        user_text = task.get("task", "")
        if not user_text:
            user_text = task.get("query", "")
        emotion = detect_emotion(user_text)
        
        emotion_context = {
            "stressed":  "User stressed lag raha hai. NOVA gentle aur supportive rahe.",
            "happy":     "User khush hai. NOVA energetic aur fun rahe.",
            "tired":     "User thaka hua hai. NOVA calm aur caring rahe.",
            "sad":       "User sad hai. NOVA bahut gentle aur empathetic rahe.",
            "excited":   "User excited hai. NOVA uski energy match kare.",
            "neutral":   "Normal friendly tone."
        }.get(emotion, "Normal friendly tone.")
        
        return AgentResult(
            agent_name="manas",
            success=True,
            data=emotion_context,
            confidence=0.8
        )

    def background_scan(self) -> Finding:
        try:
            client = chromadb.PersistentClient(path="./data/chroma")
            collection = client.get_or_create_collection(name="nova_memory")
            
            results = collection.get(limit=5)
            documents = results.get("documents", [])
            
            stress_keywords = ["deadline", "stuck", "not working", "frustrated", "help"]
            stress_detected = False
            for doc in documents:
                if any(k in doc.lower() for k in stress_keywords):
                    stress_detected = True
                    break
            
            if stress_detected:
                return Finding(
                    agent_name=self.name,
                    priority=Priority.MEDIUM,
                    title="MANAS: You seem stressed",
                    detail="Brother, take a break. A 10-minute walk would be great.",
                    action_type=ActionType.INFO_ONLY
                )
        except Exception as e:
            print(f"[BG-ERROR] MANAS: {e}")
        return None
