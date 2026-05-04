# 🌌 Lecture to Notes: Cinematic AI Processor

Transform your lecture audio into high-impact, structured study resources using local AI intelligence. Featuring a liquid-glass design and automated multi-tier note generation.

![Design Preview](https://img.shields.io/badge/Aesthetics-Cinematic-emerald)
![AI Engine](https://img.shields.io/badge/AI-Ollama%20%7C%20Whisper-blue)
![Frontend](https://img.shields.io/badge/UI-React%20%7C%20Framer%20Motion-purple)

## 🚀 Features

- **Smart Transcription**: Automated processing via OpenAI Whisper with local transcript reuse.
- **Multi-Tier Intelligence**: Automatically generates 3 formats of notes (Short, Detailed, Extreme) using LLaMA-3 or Phi-3.
- **Standard Synthesis**: Core summarization via BART for fast, efficient insights.
- **Automated Archive**: Generates PDFs and 2-stage MCQs (Questions & Answers) linked to your detailed notes.
- **Cinematic Archive**: A premium, glassmorphism-themed library to browse and download your intelligence base.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **AI Models**: Ollama (LLaMA-3, Phi-3), Transformers (BART), OpenAI Whisper
- **Frontend**: React + Vite, Framer Motion, Lucide React
- **Document Engine**: ReportLab (PDF Generation)

## 📦 Setup Instructions

### 1. Prerequisites
- Install [Python 3.10+](https://www.python.org/)
- Install [Node.js](https://nodejs.org/)
- Install [Ollama](https://ollama.com/) and pull your preferred models:
  ```bash
  ollama pull llama3.1:8b
  ollama pull phi3:latest
  ```

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AI_Class_Note_Generator.git
cd AI_Class_Note_Generator

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run the App
Simply double-click the `start_app.bat` file in the root directory to launch the entire system!

## 📂 Project Structure

- `/lectures`: Place your raw audio/video files here.
- `/notes`: Organized output folder (Transcripts, Notes, PDFs, MCQs).
- `main.py`: The AI Backend Engine.
- `start_app.bat`: One-click system initializer.

## 📜 License
MIT License. Created for students and researchers looking for a premium, local-first study tool.
