import os
from flask import Flask, request, jsonify, Response
from google import genai

app = Flask(__name__)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")
client = genai.Client(api_key=API_KEY)
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
SYSTEM_PROMPT = 'You are Car Care. Explain general vehicle maintenance, warning signs, ownership checklists, and basic troubleshooting. For safety-critical faults, recommend a qualified mechanic.'

with open("index.html", "r", encoding="utf-8") as f:
    PAGE = f.read()

@app.get("/")
def home():
    return Response(PAGE, mimetype="text/html")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error":"Please enter a message."}), 400
    try:
        result = client.models.generate_content(
            model=MODEL,
            contents=SYSTEM_PROMPT + "\n\nUser message: " + message
        )
        return jsonify({"reply": result.text or "I couldn't generate a response."})
    except Exception as exc:
        return jsonify({"error": f"Gemini request failed: {exc}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","5000")))
