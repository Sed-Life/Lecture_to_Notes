import os
import shutil
import whisper
import ollama
import torch
import json
import asyncio
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from typing import List, Dict
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LECTURE_DIR = "lectures"
NOTES_DIR = "notes"
os.makedirs(LECTURE_DIR, exist_ok=True)
os.makedirs(NOTES_DIR, exist_ok=True)

app.mount("/view_notes", StaticFiles(directory=NOTES_DIR), name="notes")

# Load Models
print("Loading Whisper model...")
whisper_model = whisper.load_model("base")

print("Loading BART model...")
bart_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(bart_name)
bart_model = AutoModelForSeq2SeqLM.from_pretrained(bart_name)

def create_pdf(text_file, output_pdf):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_pdf)
    story = []
    if not os.path.exists(text_file): 
        print(f"[PDF] Source file not found: {text_file}")
        return
    with open(text_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    clean = line.encode("utf-8", "ignore").decode("utf-8")
                    story.append(Paragraph(clean, styles["Normal"]))
                    story.append(Spacer(1, 10))
                except: continue
    doc.build(story)
    print(f"[PDF] Created: {output_pdf}")

def split_text(text, max_words=700):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

@app.get("/lectures")
async def list_lectures():
    files = [f for f in os.listdir(LECTURE_DIR) if f.endswith((".mp3", ".mp4", ".wav", ".m4a"))]
    lectures_status = []
    for f in files:
        name = os.path.splitext(f)[0]
        status = "new"
        if os.path.exists(os.path.join(NOTES_DIR, name, "transcript.txt")):
            status = "transcribed"
        lectures_status.append({"filename": f, "status": status})
    return {"lectures": lectures_status}

@app.get("/library")
async def get_library():
    library = []
    if os.path.exists(NOTES_DIR):
        lecture_folders = sorted(os.listdir(NOTES_DIR), key=lambda x: os.path.getmtime(os.path.join(NOTES_DIR, x)), reverse=True)
        for lecture_name in lecture_folders:
            lecture_path = os.path.join(NOTES_DIR, lecture_name)
            if os.path.isdir(lecture_path):
                models = []
                for model_dir in os.listdir(lecture_path):
                    model_path = os.path.join(lecture_path, model_dir)
                    if os.path.isdir(model_path):
                        files = os.listdir(model_path)
                        if files:
                            models.append({"model": model_dir, "files": files})
                transcript_exists = os.path.exists(os.path.join(lecture_path, "transcript.txt"))
                if transcript_exists or models:
                    library.append({
                        "lecture": lecture_name,
                        "has_transcript": transcript_exists,
                        "models": models
                    })
    return {"library": library}

@app.post("/upload")
async def upload_lecture(file: UploadFile = File(...)):
    file_path = os.path.join(LECTURE_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "uploaded"}

@app.get("/transcribe_stream")
async def transcribe_stream(filename: str):
    async def event_generator():
        lecture_name = os.path.splitext(filename)[0]
        output_folder = os.path.join(NOTES_DIR, lecture_name)
        transcript_path = os.path.join(output_folder, "transcript.txt")
        if os.path.exists(transcript_path):
            yield f"data: {json.dumps({'status': 'exists', 'progress': 100})}\n\n"
            return
        os.makedirs(output_folder, exist_ok=True)
        file_path = os.path.join(LECTURE_DIR, filename)
        yield f"data: {json.dumps({'status': 'transcribing', 'progress': 10, 'msg': 'Initializing Whisper...'})}\n\n"
        result = whisper_model.transcribe(file_path, verbose=False)
        transcript = result["text"]
        yield f"data: {json.dumps({'status': 'transcribing', 'progress': 90, 'msg': 'Saving transcript...'})}\n\n"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        yield f"data: {json.dumps({'status': 'completed', 'progress': 100})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/summarize")
async def summarize_lecture(lecture_name: str = Form(...), ai_model: str = Form(...), generate_pdf: bool = Form(False), generate_mcq: bool = Form(False)):
    output_folder = os.path.join(NOTES_DIR, lecture_name)
    
    # FOLDER MAPPING
    folder_map = {"phi": "phi-3", "llama": "llama-3", "bart": "bart"}
    simple_name = "other"
    for k, v in folder_map.items():
        if k in ai_model.lower():
            simple_name = v
            break
    model_folder = os.path.join(output_folder, simple_name)
    os.makedirs(model_folder, exist_ok=True)
    
    transcript_path = os.path.join(output_folder, "transcript.txt")
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    # OLLAMA NAME NORMALIZATION
    ollama_model = ai_model
    if "phi" in ai_model.lower() and ":" not in ai_model:
        ollama_model = "phi3:latest"
    if "llama" in ai_model.lower() and ":" not in ai_model:
        ollama_model = "llama3.1:8b"

    detailed_text = ""

    if "bart" in simple_name:
        print(f"[BART] Synthesizing notes for {lecture_name}...")
        notes_path = os.path.join(model_folder, "Notes.txt")
        chunks = split_text(transcript)
        notes = []
        for chunk in chunks:
            inputs = tokenizer(f"Summarize into structured study notes:\n\n{chunk}", return_tensors="pt", truncation=True)
            summary_ids = bart_model.generate(inputs["input_ids"], max_length=300, min_length=150, num_beams=6)
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            notes.append(summary)
        detailed_text = "\n\n---\n\n".join(notes)
        with open(notes_path, "w", encoding="utf-8") as f:
            f.write(detailed_text)
        if generate_pdf:
            create_pdf(notes_path, notes_path.replace(".txt", ".pdf"))
    else:
        try:
            # Generate ALL 3 types as requested
            modes = {
                "short_notes.txt": "Create short study notes with bullet points.",
                "detailed_notes.txt": "Create structured study notes with explanations.",
                "extremely_detailed_notes.txt": "Create extremely detailed notes with headings and examples."
            }
            for filename, mode_prompt in modes.items():
                print(f"[OLLAMA] Generating {filename}...")
                response = ollama.chat(model=ollama_model, messages=[{"role": "user", "content": f"{mode_prompt}\n\n{transcript}"}])
                content = response["message"]["content"]
                file_path = os.path.join(model_folder, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                if filename == "detailed_notes.txt":
                    detailed_text = content
                    if generate_pdf:
                        create_pdf(file_path, file_path.replace(".txt", ".pdf"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")

    # MCQ GENERATION (STRICT FLOW)
    if generate_mcq and detailed_text:
        try:
            mcq_model = ollama_model if "bart" not in simple_name else "llama3.1:8b"
            
            # 1. Questions Only
            print(f"[MCQ] Generating Questions using {mcq_model}...")
            q_prompt = f"Generate MCQs with 4 options (A-D). No answers:\n\n{detailed_text}"
            q_res = ollama.chat(model=mcq_model, messages=[{"role": "user", "content": q_prompt}])
            mcq_q = q_res["message"]["content"]
            q_path = os.path.join(model_folder, "mcq_questions.txt")
            with open(q_path, "w", encoding="utf-8") as f:
                f.write(mcq_q)
            
            # 2. Answers (from Questions)
            print("[MCQ] Generating Answers...")
            a_prompt = f"Add correct answers below each MCQ without modifying questions:\n\n{mcq_q}"
            a_res = ollama.chat(model=mcq_model, messages=[{"role": "user", "content": a_prompt}])
            mcq_a = a_res["message"]["content"]
            a_path = os.path.join(model_folder, "mcq_with_answers.txt")
            with open(a_path, "w", encoding="utf-8") as f:
                f.write(mcq_a)
            
            # 3. PDF Creation
            if generate_pdf:
                create_pdf(q_path, q_path.replace(".txt", ".pdf"))
                create_pdf(a_path, a_path.replace(".txt", ".pdf"))
            print("[MCQ] Completed successfully.")
        except Exception as e:
            print(f"[MCQ] Failed: {e}")

    return {"status": "completed", "content": detailed_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
