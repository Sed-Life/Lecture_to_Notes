import whisper
import os
import ollama
import time
import sys
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# -----------------------------
# Load Whisper
# -----------------------------
print("Loading Whisper model...")
whisper_model = whisper.load_model("medium")


# -----------------------------
# Load BART
# -----------------------------
print("Loading BART summarization model...")
bart_model_name = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(bart_model_name)
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(bart_model_name)


# -----------------------------
# Split transcript
# -----------------------------
def split_text(text, max_words=700):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i + max_words]))
    return chunks


# -----------------------------
# PDF Creator
# -----------------------------
def create_pdf(file_path, output_pdf):

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_pdf)
    story = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line:
            try:
                clean = line.encode("utf-8", "ignore").decode("utf-8")
                story.append(Paragraph(clean, styles["Normal"]))
                story.append(Spacer(1, 10))
            except:
                continue

    doc.build(story)


# -----------------------------
# Ensure model exists
# -----------------------------
def ensure_model(model_name):

    print(f"[INFO] Checking model: {model_name}")

    try:
        models = ollama.list()
        installed = [m["name"] for m in models["models"]]

        if model_name in installed:
            print("[OK] Model already installed\n")
            return

        print(f"[DOWNLOAD] Pulling {model_name}...\n")
        os.system(f"ollama pull {model_name}")

    except Exception:
        print("[WARNING] Could not verify model list.")


# -----------------------------
# Wait for Ollama
# -----------------------------
def wait_for_ollama(model_name):

    print("\n[INFO] Checking AI engine...")

    for _ in range(20):
        try:
            ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": "ping"}]
            )
            print("[READY] AI engine connected\n")
            return
        except:
            time.sleep(1)

    print("\n[ERROR] Ollama not responding.")
    sys.exit()


# -----------------------------
# LLM Generator
# -----------------------------
def generate_llm(text, model_name, mode):

    if mode == "short":
        instruction = "Create short study notes with bullet points."

    elif mode == "detailed":
        instruction = "Create structured study notes with explanations."

    elif mode == "extreme":
        instruction = "Create extremely detailed notes with headings and examples."

    elif mode == "mcq":
        instruction = "Generate MCQs with 4 options (A-D). No answers."

    elif mode == "mcq_from_questions":
        instruction = "Add correct answers below each MCQ without modifying questions."

    prompt = f"{instruction}\n\n{text}"

    try:
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"num_ctx": 4096}
        )
        return response["message"]["content"]

    except:
        time.sleep(1)
        return generate_llm(text, model_name, mode)


# -----------------------------
# Select Lecture
# -----------------------------
lecture_folder = "lectures"

files = [f for f in os.listdir(lecture_folder)
         if f.endswith((".mp3", ".mp4", ".wav", ".m4a"))]

if not files:
    print("No lecture files found.")
    sys.exit()

print("\nAvailable lectures:\n")
for i, file in enumerate(files, start=1):
    print(f"{i}. {file}")

choice = int(input("\nSelect lecture number: "))
selected_file = files[choice - 1]

lecture_path = os.path.join(lecture_folder, selected_file)
lecture_name = os.path.splitext(selected_file)[0]

print(f"\nSelected lecture: {selected_file}")


# -----------------------------
# Folder setup
# -----------------------------
base_folder = os.path.join("notes", lecture_name)
os.makedirs(base_folder, exist_ok=True)

transcript_path = os.path.join(base_folder, "transcript.txt")


# -----------------------------
# Model selection
# -----------------------------
print("\nSelect AI Model:")
print("1. BART")
print("2. Phi-3")
print("3. LLaMA-3")

model_choice = int(input("\nChoice: "))


# =====================================================
# BART
# =====================================================
if model_choice == 1:

    model_folder = os.path.join(base_folder, "bart")
    os.makedirs(model_folder, exist_ok=True)

    notes_path = os.path.join(model_folder, "Notes.txt")

    if os.path.exists(notes_path):
        print("\nNotes already exist → Skipping")
        sys.exit()

    if not os.path.exists(transcript_path):

        detect = whisper_model.transcribe(lecture_path)
        lang = detect["language"]

        result = whisper_model.transcribe(
            lecture_path, task="translate"
        ) if lang != "en" else detect

        transcript = result["text"]

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

    else:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()

    chunks = split_text(transcript)

    notes = []

    print("\nGenerating BART notes...")

    for chunk in chunks:

        formatted_chunk = (
            "Summarize into structured study notes with explanations:\n\n" + chunk
        )

        inputs = tokenizer(formatted_chunk, return_tensors="pt", truncation=True)

        summary_ids = summarizer_model.generate(
            inputs["input_ids"],
            max_length=300,
            min_length=150,
            num_beams=6,
            length_penalty=1.5
        )

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        notes.append(summary)

    with open(notes_path, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(notes))

    print("\nBART Notes Created.")
    sys.exit()


# =====================================================
# PHI / LLAMA
# =====================================================
model_name = "phi3" if model_choice == 2 else "llama3.1:8b"

ensure_model(model_name)
wait_for_ollama(model_name)

model_folder = os.path.join(base_folder, "phi3" if model_choice == 2 else "llama3")
os.makedirs(model_folder, exist_ok=True)

detailed_path = os.path.join(model_folder, "detailed_notes.txt")
mcq_ans_path = os.path.join(model_folder, "mcq_with_answers.txt")

detailed_pdf = detailed_path.replace(".txt", ".pdf")
mcq_pdf = mcq_ans_path.replace(".txt", ".pdf")

notes_exist = os.path.exists(detailed_path)
mcq_exists = os.path.exists(mcq_ans_path)
pdf_exists = os.path.exists(detailed_pdf)


# -----------------------------
# EXISTING FLOW
# -----------------------------
if notes_exist:

    print("\nNotes already exist → Reusing")

    if mcq_exists:
        print("MCQ already exists → Skipping")
        mcq_choice = "n"
    else:
        mcq_choice = input("\nGenerate MCQ? (y/n): ")

    if pdf_exists:
        print("PDF already exists → Skipping PDF generation")
        print("\nDone.")
        sys.exit()

    pdf_choice = input("Generate PDF? (y/n): ")

    with open(detailed_path, "r", encoding="utf-8", errors="ignore") as f:
        detailed_text = f.read()

    if mcq_choice.lower() == "y" and not mcq_exists:

        print("\nGenerating MCQs...")

        mcq_q = generate_llm(detailed_text, model_name, "mcq")

        with open(os.path.join(model_folder, "mcq_questions.txt"), "w", encoding="utf-8") as f:
            f.write(mcq_q)

        mcq_a = generate_llm(mcq_q, model_name, "mcq_from_questions")

        with open(mcq_ans_path, "w", encoding="utf-8") as f:
            f.write(mcq_a)

    if pdf_choice.lower() == "y":

        print("\nCreating PDFs...")

        create_pdf(detailed_path, detailed_pdf)

        if os.path.exists(mcq_ans_path):
            create_pdf(mcq_ans_path, mcq_pdf)

    print("\nDone.")
    sys.exit()


# -----------------------------
# NEW FLOW
# -----------------------------
mcq_choice = input("\nGenerate MCQ? (y/n): ")
pdf_choice = input("Generate PDF? (y/n): ")

if not os.path.exists(transcript_path):

    detect = whisper_model.transcribe(lecture_path)
    lang = detect["language"]

    result = whisper_model.transcribe(
        lecture_path, task="translate"
    ) if lang != "en" else detect

    transcript = result["text"]

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)

else:
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

chunks = split_text(transcript)

short_notes = []
detailed_notes = []
extreme_notes = []

print("\nGenerating notes...")

for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}/{len(chunks)}")

    short_notes.append(generate_llm(chunk, model_name, "short"))
    detailed_notes.append(generate_llm(chunk, model_name, "detailed"))
    extreme_notes.append(generate_llm(chunk, model_name, "extreme"))

with open(os.path.join(model_folder, "short_notes.txt"), "w", encoding="utf-8") as f:
    f.write("\n\n".join(short_notes))

detailed_text = "\n\n".join(detailed_notes)

with open(detailed_path, "w", encoding="utf-8") as f:
    f.write(detailed_text)

with open(os.path.join(model_folder, "extremely_detailed_notes.txt"), "w", encoding="utf-8") as f:
    f.write("\n\n".join(extreme_notes))


# MCQ
if mcq_choice.lower() == "y":

    print("\nGenerating MCQs...")

    mcq_q = generate_llm(detailed_text, model_name, "mcq")

    with open(os.path.join(model_folder, "mcq_questions.txt"), "w", encoding="utf-8") as f:
        f.write(mcq_q)

    mcq_a = generate_llm(mcq_q, model_name, "mcq_from_questions")

    with open(mcq_ans_path, "w", encoding="utf-8") as f:
        f.write(mcq_a)


# PDF
if pdf_choice.lower() == "y":

    if os.path.exists(detailed_pdf):
        print("PDF already exists → Skipping")
    else:
        print("\nCreating PDFs...")

        create_pdf(detailed_path, detailed_pdf)

        if os.path.exists(mcq_ans_path):
            create_pdf(mcq_ans_path, mcq_pdf)


print("\nDone.")