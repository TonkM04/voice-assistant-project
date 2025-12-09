import pyaudio
import wave
import struct
import time
import keyboard
import pyttsx3
from transformers import pipeline
import pvporcupine
from vosk import Model, KaldiRecognizer
import json
import os


# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
ACCESS_KEY = "Pgl6vN7wjS4Xpd+fvQ1MR62c+uApzFiuEDz728YiKlz5u0mecgUxeg=="
WAKEWORD_PATH = "Sweetheart.ppn"
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"
QUESTION_FILE = "question.wav"

RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024


# -------------------------------------------------------
# LOAD Q&A MODEL
# -------------------------------------------------------
print("Loading Q&A model...")
generator = pipeline("text2text-generation", model="google/flan-t5-base")
print("System ready!")
print("-------------------------------------------------------")


# -------------------------------------------------------
# TTS FUNCTION — guaranteed stable every time
# -------------------------------------------------------
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    del engine    # <---- KEY FIX: release audio device fully


# -------------------------------------------------------
# RECORD UNTIL SPACE
# -------------------------------------------------------
def record_until_space(filename):
    print("Press SPACE to start recording...")
    keyboard.wait("space")
    print("Recording... Press SPACE again to stop.")

    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                     input=True, frames_per_buffer=CHUNK)

    frames = []
    time.sleep(0.3)

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        if keyboard.is_pressed("space"):
            print("Recording stopped.")
            break

    stream.stop_stream()
    stream.close()
    pa.terminate()

    # save wav
    wf = wave.open(filename, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    print("Saved:", filename)


# -------------------------------------------------------
# WAKE WORD DETECTION
# -------------------------------------------------------
def wait_for_wake_word():
    print("Listening for wake word...")

    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[WAKEWORD_PATH]
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm) >= 0:
            print("Wake word detected!")
            break

    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()


# -------------------------------------------------------
# SPEECH → TEXT (VOSK)
# -------------------------------------------------------
def transcribe(filename):
    if not os.path.exists(VOSK_MODEL_PATH):
        raise FileNotFoundError("Vosk model not found.")

    model = Model(VOSK_MODEL_PATH)
    wf = wave.open(filename, "rb")
    recognizer = KaldiRecognizer(model, wf.getframerate())

    text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break

        if recognizer.AcceptWaveform(data):
            res = json.loads(recognizer.Result())
            text += res.get("text", "") + " "

    final = json.loads(recognizer.FinalResult())
    text += final.get("text", "")

    return text.strip()


# -------------------------------------------------------
# MAIN LOOP
# -------------------------------------------------------
while True:
    wait_for_wake_word()

    record_until_space(QUESTION_FILE)

    question = transcribe(QUESTION_FILE)
    print("You said:", question)

    if question.strip() == "":
        answer = "I could not understand. Please try again."
    else:
        prompt = f"Answer the question clearly:\nQuestion: {question}\nAnswer:"
        out = generator(prompt, max_new_tokens=60)
        answer = out[0]["generated_text"].replace(prompt, "").strip()

    print("Assistant:", answer)
    speak(answer)
