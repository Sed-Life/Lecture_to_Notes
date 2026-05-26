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

## 📦 Setup Instructions (For Absolute Beginners)

Don't worry if you've never coded before! Just follow these steps one by one:

### Step 1: Install the Required Software
Before we download the app, your computer needs a few basic tools:
1. **Python**: [Download Python here](https://www.python.org/downloads/). *(IMPORTANT: When installing, make sure to check the box that says **"Add python.exe to PATH"** at the very bottom of the installer window!)*
2. **Node.js**: [Download Node.js here](https://nodejs.org/). (Just install it normally by clicking "Next" through the installer).
3. **Ollama**: [Download Ollama here](https://ollama.com/). (This is the engine that runs the AI on your computer).
4. **FFmpeg**: (This is required for the transcription model to process audio/video files). 
   * **Easy Install**: Open your terminal (`cmd`) and run this command:
     `winget install --id=Gyan.FFmpeg -e --source winget`
   * *(Note: After installing FFmpeg, you MUST close and reopen your command prompt/terminal window so it registers the change!).*

### Step 2: Download the AI Models
Once Ollama is installed, we need to download the "brain" of the AI.
1. Open a terminal on your computer (Press your Windows key, type `cmd`, and press Enter).
2. Type this exact command and press Enter:
   `ollama pull llama3.1:8b`
3. Wait for it to finish downloading. Then, type this and press Enter:
   `ollama pull phi3:latest`

### Step 3: Download this App (Cloning)
Now we will download the Lecture to Notes app itself!
1. In your terminal (`cmd`), type the following to download the app to your computer:
   `git clone https://github.com/Sed-Life/Lecture_to_Notes.git`
2. Once it finishes downloading, type this to go inside the folder you just downloaded:
   `cd Lecture_to_Notes`

### Step 4: Install Dependencies
The app needs a few extra packages to run properly. Let's install them:
1. In the same terminal (make sure you are inside the `Lecture_to_Notes` folder), type this and press Enter:
   `pip install -r requirements.txt`
2. Next, we need to set up the visual interface (frontend). Type this and press Enter to go into the frontend folder:
   `cd frontend`
3. Now type this and press Enter:
   `npm install`

### Step 5: Start the App! 🎉
You're all done with the hard part! 
1. Open your File Explorer and go to the `Lecture_to_Notes` folder.
2. Put any of your lecture audio or video files into the `lectures` folder.
3. Simply double-click the `start_app.bat` file. This will automatically start the AI and open a beautiful web page where you can generate your notes!

## 📂 Project Structure

- `/lectures`: Place your raw audio/video files here.
- `/notes`: Organized output folder (Transcripts, Notes, PDFs, MCQs).
- `main.py`: The AI Backend Engine.
- `start_app.bat`: One-click system initializer.

## 📜 License
MIT License. Created for students and researchers looking for a premium, local-first study tool.
