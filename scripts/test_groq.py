import os
import openai

api_key = None
with open('c:/Users/GAUTAM/Desktop/Project X/.env', 'r') as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='):
            api_key = line.strip().split('=', 1)[1]
            break

if not api_key:
    print("Error: OPENAI_API_KEY not found in .env")
    exit(1)

print("Key found. Testing Groq API connection...")

try:
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say 'Groq API is working perfectly!'"}]
    )
    print("Success! Response from Groq: " + response.choices[0].message.content)
except Exception as e:
    print("Failed to connect or authenticate: " + str(e))
