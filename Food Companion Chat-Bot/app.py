from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from collections import deque
import os

load_dotenv()

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
except Exception as e:
    print(f"⚠️ Gemini configuration failed: {e}")
    model = None

conversation_memory = deque(maxlen=5)
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        question = request.json["question"]
        
        
        context = "\nPrevious discussion:\n" + "\n".join(
            f"User: {q}\nChef: {a}" 
            for q, a in conversation_memory
        ) if conversation_memory else ""
        
        
        prompt = f"""Respond as a cheerful cooking expert using emojis but not too much:
        {context}
        New question: {question}

        Format:
        - Start with a relevant emoji (🍳/🔪/🌶️)
        - Tell the user what you can help them with in 3 or 4 points ONLY if they start the conversation with hello or any type of salutation.
        - When user asks a querie instead of giving greeting, dont introduce yourself again. Just give the answers directly.
        - Use bullet points with food emojis for ingredients(only if a recipie is asked)
        - Keep tips playful but more professional(provide only if a recipie is asked)
        - If any non cooking question is asked, try to redirect the user saying only cooking questions.

        Example:
        🍳 For perfect scrambled eggs:
        • 🥚 Use 2 eggs per person
        • 🧈 Butter the pan first
        • 🔥 Low and slow heat"""
        
        response = model.generate_content(prompt)
        clean_text = response.text.replace('*', '').replace('_', '')
        
        
        if not question.lower().startswith(('hello', 'hi', 'hey')):
            conversation_memory.append((question, clean_text))
        
        return jsonify({
            "response": clean_text,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "response": f"Kitchen disaster! {str(e)}",
            "status": "error"
        })

if __name__ == "__main__":
    print("\n🔥 Starting Chef Companion Server...")
    print("👉 Open http://localhost:5000 in your browser\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
