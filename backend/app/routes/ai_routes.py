from flask import Blueprint, request, jsonify
from google.generativeai import GenerativeModel, configure
import google.generativeai as genai
from google.api_core import retry
import os

ai_bp = Blueprint("ai", __name__, url_prefix="/api")

# Konfiguracja z retry (globalna)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("BRAK GEMINI_API_KEY w env!")
else:
    configure(api_key=api_key)


@ai_bp.route("/ask", methods=["POST"])
def ask_gemini():
    try:
        if not request.is_json:
            return jsonify({"error": "JSON wymagany"}), 400

        data = request.get_json()
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "Podaj pytanie"}), 400

        model = GenerativeModel(
            "gemini-2.5-flash",  
            generation_config={"temperature": 0.7, "max_output_tokens": 1024},
        )

        r = retry.Retry(initial=1.0, multiplier=2.0, maximum=60.0, deadline=120.0)
        response = model.generate_content(question, request_options={"retry": r})

        return jsonify({"answer": response.text})

    except Exception as e:
        print(f"Błąd /ask: {str(e)}")
        return jsonify({"error": "Błąd serwera (sprawdź logi)"}), 500
