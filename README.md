Voice Assistant Project

This project is a simple local voice assistant that can wake up with a custom keyword, record a question from the user, convert it into text, generate an answer, and speak the answer out loud.
Everything runs offline except the language model, which uses a local HuggingFace pipeline.

The main goal of this project was to understand how a full audio pipeline works—from wake-word detection to speech recognition, question-answering, and text-to-speech—and to get a stable version running end to end.

Features

Wake-word detection using Porcupine

Recording audio on demand

Speech-to-text using the Vosk offline model

Answer generation with FLAN-T5

Text-to-speech using pyttsx3

All components run locally

Motivation and Notes

During development, the biggest challenges were related to audio handling.
Different modules (wake-word engine, STT, and TTS) all try to use the microphone or speaker, and they do not always release the device correctly.
This caused issues such as:

TTS speaking only the first time

Microphone streams blocking each other

Wake-word detection not starting after STT

I spent a lot of time debugging these problems and eventually revised the structure so that every audio component opens and closes cleanly. This made the system much more stable.

Although the assistant does not yet perform well in very noisy environments, and speaker identification is not implemented, the full pipeline works reliably and demonstrates the direction the project is going.

File Structure
assistant.py          # Main program
Sweetheart.ppn        # Custom wake-word file
requirements.txt
README.md


You will also need the Vosk model:

vosk-model-small-en-us-0.15/


(This folder is too large to upload to GitHub.)

How to Run

Install the required packages:

pip install -r requirements.txt


Download and extract the Vosk model folder next to assistant.py.

Run the assistant:

python assistant.py

What Works Now

Wake-word detection

Recording on space-key press

Transcription of the recorded audio

Generating an answer with FLAN-T5

Speaking the answer out loud every time

The “TTS only speaks once” issue has been fixed by reinitializing and releasing the TTS engine properly each time.

What Still Needs Improvement

More accurate recognition in noisy environments

Distinguishing the intended speaker from background speech

Better noise reduction

Faster response time on smaller devices

These were part of the original plan, and I will continue exploring them.

Reflection

Even though not every feature is fully completed, the project taught me a lot about audio pipelines, resource conflicts, and debugging real-world problems.
Getting a stable end-to-end system running was my main focus, and this version reflects the progress made so far.
