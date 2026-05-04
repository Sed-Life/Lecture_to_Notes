from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

print("Loading summarization model...")

model_name = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

print("Reading transcript...")

with open("transcript.txt", "r", encoding="utf-8") as f:
    text = f.read()

inputs = tokenizer(
    text,
    max_length=1024,
    return_tensors="pt",
    truncation=True
)

print("Generating lecture notes...")

summary_ids = model.generate(
    inputs["input_ids"],
    max_length=200,
    min_length=80,
    num_beams=4,
    early_stopping=True
)

notes = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

print("\n----- LECTURE NOTES -----\n")
print(notes)

with open("notes.txt", "w", encoding="utf-8") as f:
    f.write(notes)

print("\nNotes saved as notes.txt")