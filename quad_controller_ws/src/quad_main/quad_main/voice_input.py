import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

q = queue.Queue()

commands = [
    "forward",
    "backward",
    "up",
    "down",
    "left",
    "right",
    "stop"
]

model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000, json.dumps(commands + ["[unk]"]))

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def voice_input():
    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=audio_callback
    ):
        print("Listening...")

        while True:
            data = q.get()

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())

                print(str(result["text"]))