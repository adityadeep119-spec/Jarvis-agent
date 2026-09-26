# Save as record_voice.py and run: python record_voice.py
import wave
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "master_voice.wav"

p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
)

print("* Recording vocal biometric sample... Speak normally for 5 seconds.")
frames = [
    stream.read(CHUNK)
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS))
]
print("* Baseline voice profile captured.")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b"".join(frames))
wf.close()