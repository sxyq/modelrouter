from transformers import AutoTokenizer, AutoModelForSequenceClassification
name = "distilbert-base-uncased-finetuned-sst-2-english"
dest = "/app/model_cache/sentiment_model"
print("Downloading tokenizer...", flush=True)
tok = AutoTokenizer.from_pretrained(name)
tok.save_pretrained(dest)
print("Downloading model...", flush=True)
model = AutoModelForSequenceClassification.from_pretrained(name)
model.save_pretrained(dest)
print("DONE", flush=True)
