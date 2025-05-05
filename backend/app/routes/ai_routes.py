from flask import Blueprint, request, jsonify
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os

ai_bp = Blueprint("ai", __name__, url_prefix="/api")

try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception as e:
    print(f"Błąd inicjalizacji Gemini API: {str(e)}")


@ai_bp.route("/ask", methods=["POST"])
def ask_gemini():
    try:
        if not request.is_json:
            return jsonify({"error": "Żądanie musi być w formacie JSON"}), 400

        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "Brak pytania w żądaniu"}), 400

        model = GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(question)

        return jsonify({"answer": response.text})

    except Exception as e:
        print(f"Błąd w endpointcie /ask: {str(e)}")
        return jsonify({"error": "Wewnętrzny błąd serwera"}), 500
