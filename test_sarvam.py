import httpx
import os
from dotenv import load_dotenv

load_dotenv()

def test_chat():
    key = os.getenv("SARVAM_TTS_KEY") # We used this for Chat too
    print(f"Testing Chat with key: {key[:5]}...")
    url = "https://api.sarvam.ai/v1/chat/completions"
    headers = {
        "api-subscription-key": key,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sarvam-m",
        "messages": [{"role": "user", "content": "Hii, how are you?"}]
    }
    
    headers_list = [
        {"api-subscription-key": key},
        {"Authorization": f"Bearer {key}"},
        {"Authorization": key},
        {"x-api-key": key}
    ]
    
    for i, h in enumerate(headers_list):
        h["Content-Type"] = "application/json"
        try:
            print(f"Trying Header Set {i+1}: {list(h.keys())[0]}")
            response = httpx.post(url, json=payload, headers=h, timeout=10)
            print(f"  Code: {response.status_code}")
            if response.status_code == 200:
                print(f"  SUCCESS with {list(h.keys())[0]}!")
                print(f"  Response: {response.text[:100]}")
                return
        except Exception as e:
            print(f"  Error: {e}")

def test_stt():
    key = os.getenv("SARVAM_STT_KEY")
    print(f"\nTesting STT with key: {key[:5]}...")
    url = "https://api.sarvam.ai/speech-to-text"
    # Note: STT usually requires multipart/form-data, but we'll test auth first
    headers = {"api-subscription-key": key}
    try:
        # Just a dummy request to check auth
        response = httpx.post(url, headers=headers, timeout=10)
        print(f"STT Auth Check Code: {response.status_code}")
    except Exception as e:
        print(f"STT Error: {e}")

if __name__ == "__main__":
    test_chat()
    print("-" * 30)
    test_stt()
