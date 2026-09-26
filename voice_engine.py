import pyttsx3
import speech_recognition as sr

def speak(text: str):
    """Converts text to speech aloud with a fresh engine instance and safe COM handling."""
    print(f"[Jarvis Voice]: {text}")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 175)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Speech Error: {str(e)}")

def listen_to_user() -> str:
    """Listens naturally via microphone until you finish speaking (no rigid time limits)."""
    print("\n[Listening for your command, Sir... Speak now]")
    r = sr.Recognizer()
    r.pause_threshold = 2.5
    with sr.Microphone() as source:
        # Adjust slightly for background room noise
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Listens dynamically until you pause (allows long sentences up to 15 seconds)
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            text = r.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            print("[Listening timed out, Sir]")
            return ""
        except sr.UnknownValueError:
            print("[Could not understand audio, Sir]")
            return ""
        except Exception as e:
            print(f"Listening Error: {str(e)}")
            return ""