import pyttsx3


def speak_response(text: str):
  """Synthesizes voice output locally using Windows speech engines."""
  try:
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)  # Speech speed
    engine.setProperty("volume", 1.0)  # Full volume

    engine.say(text)
    engine.runAndWait()
  except Exception as e:
    print(f"Speech synthesis error: {e}")


if __name__ == "__main__":
  print("Testing voice speaker...")
  speak_response(
      "Audio protocols active and fully operational, sir. How can I assist"
      " you?"
  )