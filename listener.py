import os
import speech_recognition as sr
import whisper

print("[INITIALIZING LOCAL STT ENGINE...]")
local_stt = whisper.load_model("tiny")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("\n--- Awaiting Voice Input ---")
        print("[Listening... Speak now]")
        # Change r.listen(source) to include timeout limits:
        audio = r.listen(source, timeout=3, phrase_time_limit=5)

    try:
        # Online cloud recognition
        text = r.recognize_google(audio)
        return text
    except Exception as e:
        # Catches ALL network timeouts, socket disconnects, and API failures
        print(f"[Network Offline/Error: Switching to local Whisper STT...]")
        temp_wav = "temp_voice.wav"
        with open(temp_wav, "wb") as f:
            f.write(audio.get_wav_data())
        
        result = local_stt.transcribe(temp_wav)
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
            
        return result.get("text", "").strip()