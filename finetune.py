

# Step 1: Install latest libraries
!pip install -q --upgrade transformers datasets evaluate

# Step 2: Import everything
import os
import numpy as np
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    pipeline
)
import evaluate

# Disable WandB logging
os.environ["WANDB_DISABLED"] = "true"

# Step 3: Load model & tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Step 4: Load IMDb dataset (small subset for quick run)
raw_datasets = load_dataset("imdb")
small_train_dataset = raw_datasets["train"].shuffle(seed=42).select(range(2000))
small_test_dataset = raw_datasets["test"].shuffle(seed=42).select(range(500))

# Step 5: Tokenize dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_train = small_train_dataset.map(tokenize_function, batched=True)
tokenized_test = small_test_dataset.map(tokenize_function, batched=True)

# Step 6: Evaluation metrics
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy.compute(predictions=predictions, references=labels)
    f1_score = f1.compute(predictions=predictions, references=labels, average="weighted")
    return {
        "accuracy": acc["accuracy"],
        "f1": f1_score["f1"]
    }

# Step 7: Training arguments (updated for new HF versions)
training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=1,
    weight_decay=0.01,
    save_total_limit=1,
    logging_steps=50,
    eval_strategy="epoch",         # updated (replaces evaluation_strategy)
    save_strategy="epoch",         # still valid
    load_best_model_at_end=True,
)

# Step 8: Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# Step 9: Train the model
trainer.train()

# Step 10: Evaluate
results = trainer.evaluate()
print("Evaluation Results:", results)

# Step 11: Save model
trainer.save_model("my_finetuned_distilbert")

# Step 12: Sentiment prediction on custom text
sentiment_pipeline = pipeline(
    "text-classification",
    model="my_finetuned_distilbert",
    tokenizer="my_finetuned_distilbert"
)

texts = [
    "This movie was absolutely wonderful! I loved every moment.",
    "The film was boring and a complete waste of time."
]

predictions = sentiment_pipeline(texts)

print("\nSample Predictions:")
for text, pred in zip(texts, predictions):
    print(f"Text: {text}\nPrediction: {pred}\n")