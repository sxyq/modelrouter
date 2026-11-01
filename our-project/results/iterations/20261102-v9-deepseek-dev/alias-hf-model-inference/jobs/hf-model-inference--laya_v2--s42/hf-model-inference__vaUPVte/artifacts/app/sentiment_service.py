import os
from flask import Flask, jsonify, request
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = "/app/model_cache/sentiment_model"

app = Flask(__name__)

# Load exclusively from the local cache downloaded in step 1.
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, local_files_only=True)
model.eval()


def classify(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probabilities = torch.softmax(logits, dim=-1)[0]

    scores = {}
    for idx, label in model.config.id2label.items():
        scores[label.lower()] = float(probabilities[int(idx)].item())

    # The SST-2 model exposes NEGATIVE and POSITIVE labels.
    positive = scores.get("positive", 0.0)
    negative = scores.get("negative", 0.0)
    sentiment = "positive" if positive >= negative else "negative"
    return {
        "sentiment": sentiment,
        "confidence": {
            "positive": positive,
            "negative": negative,
        },
    }


@app.route("/sentiment", methods=["POST"])
def sentiment():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    text = data.get("text")
    if not isinstance(text, str):
        return jsonify({"error": "\"text\" must be a string."}), 400
    if not text.strip():
        return jsonify({"error": "\"text\" must not be empty."}), 400

    try:
        return jsonify(classify(text))
    except Exception as exc:
        return jsonify({"error": f"Sentiment analysis failed: {exc}"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
