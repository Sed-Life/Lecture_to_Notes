import whisper
import os

print("Loading Whisper model...")

model = whisper.load_model("large")

# Ask user for file name
file_path = input("Enter audio/video file name (mp3/mp4/wav): ")

# Check if file exists
if not os.path.exists(file_path):
    print("File not found!")
    exit()

print("Transcribing...")

result = model.transcribe(file_path)

text = result["text"]

print("\n----- TRANSCRIPT -----\n")
print(text)

# Save transcript
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("\nTranscript saved as transcript.txt")