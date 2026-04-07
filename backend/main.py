from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os

app = FastAPI()

#  ENV VARIABLES (Railway)
GROK_API_KEY = os.getenv("GROK_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = "mytoken"


# ==============================
#  GROK FUNCTION
# ==============================
def call_llm(user_msg: str):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": "You are a helpful AI therapist. Keep replies short and supportive."},
            {"role": "user", "content": user_msg}
        ],
        "max_tokens": 300
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "Sorry, I'm having trouble responding right now."

# ==============================
#  SEND WHATSAPP MESSAGE
# ==============================
def send_whatsapp_message(to: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }

    requests.post(url, headers=headers, json=data)


# ==============================
#  OPTIONAL TEST API
# ==============================
class Query(BaseModel):
    message: str

@app.post("/ask")
async def ask(query: Query):
    response = call_llm(query.message)
    return {"response": response}


# ==============================
#  WHATSAPP WEBHOOK VERIFY
# ============================
@app.get("/webhook")
def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    challenge = request.query_params.get("hub.challenge")
    verify_token = request.query_params.get("hub.verify_token")

    if mode == "subscribe" and verify_token == VERIFY_TOKEN:
        return int(challenge)

    return "Verification failed"


# ==============================
#  RECEIVE MESSAGE FROM WHATSAPP
# ==============================
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return {"status": "no message"}

        message = value["messages"][0]

        if "text" not in message:
            return {"status": "not text message"}

        user_msg = message["text"]["body"]
        sender = message["from"]

        print("User:", user_msg)

        ai_reply = call_llm(user_msg)

        print("AI:", ai_reply)

        send_whatsapp_message(sender, ai_reply)

    except Exception as e:
        print("Error:", e)

    return {"status": "ok"}