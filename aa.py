from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model + tokenizer
model = AutoModelForSequenceClassification.from_pretrained("./my_model")
tokenizer = AutoTokenizer.from_pretrained("./my_model")

# Sample text
texts = [
    "This movie was fantastic, I really loved it!",
    "Worst film ever. Totally boring!",
     "Tamil movie naala erku","raj movie 2nd half joke not good"
]

# Encode
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

# Predict
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

# Print results
for text, pred in zip(texts, predictions):
    label = pred.argmax().item()
    score = pred.max().item()
    print(f"Text: {text}")
    print(f"Prediction: LABEL_{label}, Score: {score:.4f}\n")