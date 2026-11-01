import os
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
save_dir = "/app/model_cache/sentiment_model"
os.makedirs(save_dir, exist_ok=True)
print("Starting model download...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
print("Saving model...", flush=True)
tokenizer.save_pretrained(save_dir)
model.save_pretrained(save_dir)
with open("/app/model_cache/download_complete", "w") as f:
    f.write("ok\n")
print("DONE", flush=True)
