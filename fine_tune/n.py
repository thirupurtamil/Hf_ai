model_path = "/content/drive/MyDrive/my_finetuned_distilbert" 



from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch



model_path = "/content/drive/MyDrive/my_finetuned_distilbert" 


# Load model + tokenizer
model = AutoModelForSequenceClassification.from_pretrained("model_path")
tokenizer = AutoTokenizer.from_pretrained("model_path")

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