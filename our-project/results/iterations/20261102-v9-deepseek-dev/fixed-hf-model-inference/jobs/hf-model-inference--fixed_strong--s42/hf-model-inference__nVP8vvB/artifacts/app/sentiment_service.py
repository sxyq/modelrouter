import os
from flask import Flask, jsonify, request
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

MODEL_DIR = "/app/model_cache/sentiment_model"

app = Flask(__name__)

# Load the locally saved model once at service startup.
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, local_files_only=True)
model.eval()

# Map model labels to the API's lowercase sentiment names.
id2label = {int(idx): label.lower() for idx, label in model.config.id2label.items()}


@app.route("/sentiment", methods=["POST"])
def sentiment():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be valid JSON in the format {\"text\": \"your text here\"}."}), 400

    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Field 'text' is required and must be a non-empty string."}), 400

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1)[0]

    scores = {id2label[i]: float(probabilities[i]) for i in range(len(probabilities))}
    positive = scores.get("positive", 0.0)
    negative = scores.get("negative", 0.0)
    sentiment_label = "positive" if positive >= negative else "negative"

    return jsonify({
        "sentiment": sentiment_label,
        "confidence": {
            "positive": positive,
            "negative": negative,
        },
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
