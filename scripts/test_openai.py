import os
# pyrefly: ignore [missing-import]
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

print("Key found. Testing API connection...")

try:
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'API is working'"}],
        max_tokens=10
    )
    print("Success! Response from OpenAI: " + response.choices[0].message.content)
except Exception as e:
    print("Failed to connect or authenticate: " + str(e))
