import requests
import os

GROK_API_KEY = os.getenv("GROK_API_KEY")

def call_grok(user_msg):
    url = "https://api.x.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are a helpful AI therapist."},
            {"role": "user", "content": user_msg}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]