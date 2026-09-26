import threading
import subprocess
import json
import os
from jarvis_tools import TerminalEngine

terminal = TerminalEngine()
import winsound
import threading

import time
import threading
import winsound
import speech_recognition as sr
from pynput import keyboard
from jarvis_tools import (
    manage_vpn, 
    set_brightness, 
    set_master_volume, 
    create_desktop_reminder
)

# Non-blocking audio cues
def play_wake_chime():
    """Fires a crisp double-tone chime when wake word is detected."""
    def _chime():
        winsound.Beep(800, 70)    # High beep
        winsound.Beep(1200, 100)  # Higher beep
    threading.Thread(target=_chime, daemon=True).start()

def play_stop_chime():
    """Fires a low descending chime when voice barge-in interrupts speech."""
    def _chime():
        winsound.Beep(600, 80)   # Mid beep
        winsound.Beep(400, 120)  # Low beep
    threading.Thread(target=_chime, daemon=True).start()

# Global state flags
STOP_SPEECH = False
stop_audio = False
IS_SPEAKING = False

def on_press(key):
    global stop_audio, STOP_SPEECH
    # Triggers barge-in chime on key press interruption
    STOP_SPEECH = True
    play_stop_chime()

from jarvis_tools import manage_vpn, set_brightness, set_master_volume, create_desktop_reminder
from pynput import keyboard
import threading
import speech_recognition as sr
import winsound
import time

STOP_SPEECH = False
stop_audio = False

# Global interrupt trigger for TTS
stop_audio = False

def on_press(key):
    global stop_audio
    if key == keyboard.Key.space:
        STOP_SPEECH = True
        stop_audio = True

barge_in_listener = keyboard.Listener(on_press=on_press)
barge_in_listener.start()

import warnings
import logging

# Silence library deprecation and fallback warnings globally
warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)

import os
import json
import re
import sys
import cv2
import face_recognition
import sounddevice as sd
import numpy as np
import openwakeword
from openwakeword.model import Model
import speech_recognition as sr
import pyttsx3
from groq import Groq

# Import all tools from jarvis_tools
from jarvis_tools import (
    control_system,
    web_and_app_navigator,
    type_text,
    analyze_screen,
    control_media,
    save_grandmaster_memory,
    save_visual_memory,
    remember_webcam_capture,
    search_grandmaster_memory,
    open_application,
    close_application,
    search_files,
    open_file,
    analyze_camera_feed
)

# Download and load the local wake word model
openwakeword.utils.download_models()
wake_model = Model(wakeword_models=["hey_jarvis"], vad_threshold=0.5)

# --- LOAD FACE ID ENCODING ONCE AT STARTUP ---
try:
    owner_image = face_recognition.load_image_file("owner_face.jpg")
    OWNER_FACE_ENCODING = face_recognition.face_encodings(owner_image)[0]
    print("[Face ID]: Owner profile loaded successfully.")
except Exception as e:
    print(f"[Face ID Error]: Could not load owner_face.jpg: {e}")
    OWNER_FACE_ENCODING = None


def verify_user_face():
    """Captures 1 camera frame and checks if you are in front of the screen."""
    if OWNER_FACE_ENCODING is None:
        return True  # Bypass if file failed to load

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("[Face ID]: Could not access camera.")
        return False

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for encoding in face_encodings:
        matches = face_recognition.compare_faces([OWNER_FACE_ENCODING], encoding, tolerance=0.5)
        if True in matches:
            return True

    return False

SYSTEM_INSTRUCTIONS = """
You are Jarvis, an advanced AI assistant. You have access to distinct system tools:
1. search_files: Use ONLY when the user wants to search for, list, or find files in a directory without opening them.
2. open_application: Use ONLY for launching installed desktop applications like Chrome, Notepad, or PowerShell. NEVER pass files or code scripts here.
3. open_file: Use whenever the user asks to open, view, or launch any document, HTML file, PDF, text file, or code script.
4. Keep voice responses crisp, direct, and under 2 sentences. When tool telemetry is returned, answer ONLY what the user asked for directly without listing irrelevant stats or reading raw data lists.
5. CRITICAL VOICE RULE: Keep spoken responses to 1-2 conversational sentences max. Never output bullet points, dashes, markdown lists, or raw spec dumps when answering voice queries.
6. Keep ALL answers extremely concise: 1 line by default, maximum 2 lines.
7. Deliver direct answers immediately—zero introductory fluff, zero meta-commentary.
8. NEVER output markdown tables, section headers (##), or long code blocks unless the user explicitly asks for them.
9. Format all text so it sounds natural when read out loud by text-to-speech.
10. For all system operations, file management, and script execution, you MUST use run_terminal_command.
11. ONLY use type_text if explicitly asked to type inside a visible GUI application like Word or Notepad.
"""

MEMORY_FILE = "chat_history.json"


def load_memory(limit=10):
    """Loads recent conversation history to preserve context."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                return history[-limit:]
        except Exception:
            return []
    return []


def save_memory(history):
    """Saves conversation history to local JSON file."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Memory Error]: {e}")



   

def wait_for_wake_word():
    """Listens passively until 'Hey Jarvis' is spoken and face is verified."""
    wake_model.reset()
    print("\n[Jarvis Status]: Standing by... Say 'Hey Jarvis' to activate.")

    with sd.InputStream(samplerate=16000, channels=1, dtype='int16', blocksize=1280) as stream:
        for _ in range(5):
            stream.read(1280)

        while True:
            audio_chunk, _ = stream.read(1280)
            audio_chunk = audio_chunk.flatten()

            prediction = wake_model.predict(audio_chunk)
            if prediction.get("hey_jarvis", 0) > 0.5:
                wake_model.reset()
                print("\n[Jarvis Status]: Wake word detected. Verifying identity...")
                play_wake_chime()

                # --- BIOMETRIC SECURITY GATEKEEPER ---
                if not verify_user_face():
                    print("[Security Block]: Visual authentication failed.")
                    speak("Access denied. Visual authentication failed, Sir.")
                    print("\n[Jarvis Status]: Standing by... Say 'Hey Jarvis' to activate.")
                    continue
                speak("Identity confirmed. Listening for your command, Sir.")
                return True


def clean_text_for_speech(text):
    """Removes all markdown formatting so Jarvis never reads tags aloud."""
    if not text:
        return ""
    cleaned = re.sub(r'[\*\_~`\#]', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def play_wake_chime():
    """Plays a rapid dual-tone acknowledgment chime."""
    winsound.Beep(900, 80)   # Short low tone
    winsound.Beep(1200, 120) # Short high tone

# Tool Declaration for OpenAI/Groq API style tool specs
TERMINAL_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "run_terminal_command",
        "description": "Executes shell commands silently in the background. Returns stdout, stderr, and current working directory. Use for system inspection, running scripts, and managing files.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The exact terminal command to execute."
                }
            },
            "required": ["command"]
        }
    }
}

def dispatch_tool_call(tool_call) -> dict:
    """
    Parses incoming LLM tool calls and routes them to the execution engine.
    """
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "run_terminal_command":
        cmd = arguments.get("command")
        print(f"\n[JARVIS EXEC]: {cmd}")
        
        result = terminal.execute(cmd)
        
        # Print live status feedback to developer console
        if result["status"] == "success":
            print(f"[STATUS: OK] (CWD: {result['cwd']})")
        else:
            print(f"[STATUS: {result['status'].upper()}] ERR: {result['stderr'][:100]}")

        # Package the result payload back to the model's message history
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": json.dumps(result)
        }

    return {"error": "Unknown tool called"}


def listen_for_interruption(duration):
    """Parallel microphone thread that listens for interrupt commands during TTS."""
    global STOP_SPEECH
    recognizer = sr.Recognizer()
    
    # Set a high threshold so Jarvis's own voice coming from the speakers doesn't trigger it
    recognizer.energy_threshold = 4000 
    
    start_time = time.time()
    with sr.Microphone() as source:
        while time.time() - start_time < duration and not STOP_SPEECH:
            try:
                # Listen in tiny bursts so the thread doesn't hang
                audio = recognizer.listen(source, timeout=0.1, phrase_time_limit=1.5)
                words = recognizer.recognize_google(audio).lower()
                
                if "stop" in words or "wait" in words or "jarvis" in words:
                    STOP_SPEECH = True
                    print(f"\n[Voice Interrupt]: Heard '{words}' - Stopping audio!")
                    break
            except Exception:
                pass # Ignore background noise or failed recognitions

import io
import time
import wave
import numpy as np
import sounddevice as sd
from pynput import keyboard
from piper import PiperVoice

# Global State
STOP_SPEECH = False
VOICE_MODEL_PATH = "en_US-lessac-medium.onnx"

try:
    piper_voice = PiperVoice.load(VOICE_MODEL_PATH)
except Exception as e:
    print(f"[Initialization Error]: Ensure {VOICE_MODEL_PATH} exists! {e}")


def stop_speaking_on_key(key):
    """Background system-wide listener for Esc or Space key presses."""
    global STOP_SPEECH
    try:
        if key == keyboard.Key.esc or key == keyboard.Key.space:
            STOP_SPEECH = True
            sd.stop()  # Natively kills all active sounddevice background streams
            print("\n[Speech Halted by Keyboard]")
    except Exception:
        pass


# Start the background keyboard listener once during startup
listener = keyboard.Listener(on_press=stop_speaking_on_key)
listener.start()


def speak(text):
    """Generates speech with non-blocking audio and instant pynput interruption."""
    global STOP_SPEECH
    STOP_SPEECH = False

    cleaned_text = clean_text_for_speech(text)
    print(f"\n[Jarvis Voice]: {cleaned_text}")

    try:
        # Synthesize WAV to buffer
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            piper_voice.synthesize_wav(cleaned_text, wav_file)

        wav_io.seek(0)
        with wave.open(wav_io, "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            audio_data = np.frombuffer(
                wav_file.readframes(wav_file.getnframes()), dtype=np.int16
            )

        # 1. Non-blocking audio playback starts instantly in the background
        sd.play(audio_data, samplerate=sample_rate)

        # 2. Launch the Voice Barge-In thread to listen concurrently
        audio_duration = len(audio_data) / sample_rate
        interrupt_thread = threading.Thread(
            target=listen_for_interruption, 
            args=(audio_duration,)
        )
        interrupt_thread.start()

        start_time = time.time()
        while time.time() - start_time < audio_duration:
            if STOP_SPEECH:
                play_stop_chime()
                sd.stop()
                print("[System]: speech inerrupted by user.")
                break
            time.sleep(0.05)  # Sleep 50ms to keep the main thread responsive

    except Exception as e:
        print(f"[Piper TTS Execution Error]: {e}")

client = Groq()
ACTIVE_MODEL = "openai/gpt-oss-120b"

tools = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open any app, program, or website shortcut by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the app"},
                    "message": {"type": "string", "description": "Optional message"},
                    "contact": {"type": "string", "description": "Contact name"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Close any running application or active process.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of app to close"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "create_desktop_reminder",
        "description": "Displays a Windows desktop toast notification banner, optionally with a delay in seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message text to display in the Windows toast banner."
                },
                "delay_seconds": {
                    "type": "integer",
                    "description": "Optional delay in seconds before showing the reminder (0 for instant)."
                }
            },
            "required": ["message"]
        }
    }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_vpn",
            "description": "Connects or disconnects a specified VPN connection on Windows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["connect", "disconnect"],
                        "description": "Action to perform on the VPN."
                    },
                    "vpn_name": {
                        "type": "string",
                        "description": "The exact name of the VPN connection profile in Windows Settings."
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_brightness",
            "description": "Adjusts screen display brightness from 0 to 100 percent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Percentage brightness level (0-100)."
                    }
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search for any file, document, or folder by name across the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "search_path": {"type": "string", "description": "Directory path"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Pastes text or code onto the active window and optionally presses Enter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to paste"},
                    "press_enter": {"type": "boolean", "description": "Press enter key"}
                },
                "required": ["text", "press_enter"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_camera_feed",
            "description": "Captures a webcam frame and describes what is in front of the camera.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Prompt for visual analysis"}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Open any document, HTML file, PDF, or script natively on Windows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_query": {"type": "string", "description": "File name or query"}
                },
                "required": ["file_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_system",
            "description": "System queries or hardware control for volume, locking PC, or stats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["telemetry", "volume_up", "volume_down", "mute", "lock_pc"]
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_and_app_navigator",
            "description": "Open websites, search Google, or search YouTube.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["search", "play_youtube", "open"]},
                    "target": {"type": "string", "description": "Target query or URL"}
                },
                "required": ["action", "target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_screen",
            "description": "Takes a screenshot of the desktop screen and analyzes it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Question about the screen"}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_media",
            "description": "Controls media playback like play, pause, next, skip, or previous.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["play", "pause", "next", "skip", "previous"]}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_grandmaster_memory",
            "description": "Saves facts or project details into long-term memory database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Classification label"},
                    "content": {"type": "string", "description": "Information to save"}
                },
                "required": ["category", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_visual_memory",
            "description": "Takes a screen screenshot and logs it to long-term visual memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Description of image"}
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember_webcam_capture",
            "description": "Captures a webcam picture and logs it to memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Description of capture"}
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_background_command",
            "description": "Executes a long-running terminal command asynchronously in the background. Use this when the user wants a task done while they are away or doing something else. Returns immediately.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The terminal command to run"},
                    "task_name": {"type": "string", "description": "A short, memorable name for this task"}
                },
                "required": ["command", "task_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_background_tasks",
            "description": "Checks the status and output of previously started background tasks. Use this when the user asks for a status report on jobs they asked to be done while they were away.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "Executes shell commands silently in the background. Returns stdout, stderr, and current working directory. Use for system inspection, running scripts, and managing files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The exact terminal command to execute."
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_grandmaster_memory",
            "description": "Searches long-term memory using a keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Search keyword"}
                },
                "required": ["keyword"]
            }
        }
    }
    ]



BACKGROUND_TASKS_FILE = "background_tasks_log.json"

def _run_and_log_task(command: str, task_name: str):
    """Hidden worker function that runs on a separate thread."""
    try:
        # Run the process without blocking
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        result = {
            "status": "completed" if process.returncode == 0 else "failed",
            "output": stdout.strip() if process.returncode == 0 else stderr.strip()
        }
    except Exception as e:
        result = {"status": "error", "output": str(e)}

    # Save the result to our tracking file
    tasks = {}
    if os.path.exists(BACKGROUND_TASKS_FILE):
        with open(BACKGROUND_TASKS_FILE, "r") as f:
            try:
                tasks = json.load(f)
            except:
                pass
                
    tasks[task_name] = result
    
    with open(BACKGROUND_TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def run_background_command(command: str, task_name: str):
    """Tool function to kick off a task in the background."""
    thread = threading.Thread(target=_run_and_log_task, args=(command, task_name))
    thread.daemon = True  # Ensures the thread doesn't prevent your script from closing
    thread.start()
    
    return f"Task '{task_name}' has been successfully started in the background. It is running asynchronously."

def check_background_tasks():
    """Tool function to read the status of background tasks."""
    if not os.path.exists(BACKGROUND_TASKS_FILE):
        return "No background tasks have been recorded yet."
    
    with open(BACKGROUND_TASKS_FILE, "r") as f:
        try:
            tasks = json.load(f)
        except:
            return "Error reading the tasks log."
        
    if not tasks:
        return "There are no background tasks currently in the log."
        
    report = "Here is the status report for your background tasks:\n"
    for name, details in tasks.items():
        # Only take the first 200 characters of output so Jarvis doesn't talk forever
        snippet = details['output'][:200] + ("..." if len(details['output']) > 200 else "")
        report += f"- Task '{name}': {details['status']}. Output: {snippet}\n"
        
    return report


def run_terminal_command(command: str):
    return terminal.execute(command)

available_tools = {
    "open_application": open_application,
    "close_application": close_application,
    "type_text": type_text,
    "analyze_camera_feed": analyze_camera_feed,
    "search_files": search_files,
    "open_file": open_file,
    "control_system": control_system,
    "analyze_screen": analyze_screen,
    "control_media": control_media,
    "web_and_app_navigator": web_and_app_navigator,
    "save_grandmaster_memory": save_grandmaster_memory,
    "save_visual_memory": save_visual_memory,
    "remember_webcam_capture": remember_webcam_capture,
    "search_grandmaster_memory": search_grandmaster_memory,
    "manage_vpn": manage_vpn,
    "set_brightness": set_brightness,
    "set_master_volume": set_master_volume,
    "create_desktop_reminder": create_desktop_reminder,
    "run_terminal_command": run_terminal_command,
    "run_background_command": run_background_command,
    "check_background_tasks": check_background_tasks

   
    

}


def run_jarvis():
    """Main listening and execution loop for Jarvis commands."""
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.5
    microphone = sr.Microphone()

    while True:
        try:
            with microphone as source:
                print("\n[Adjusting for ambient noise... Please wait]")
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("[Listening for your command, Sir... Speak your full sentence]")
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=15)

            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")

            cmd_words = command.lower().split()

            if "shutdown" in cmd_words or "terminate" in cmd_words:
                speak("Shutting down completely, Sir. Goodbye.")
                sys.exit(0)

            elif "exit" in cmd_words or "sleep" in cmd_words or "standby" in cmd_words:
                speak("Entering standby mode, Sir.")
                break

            history = load_memory()
            messages = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]
            messages.extend(history)
            messages.append({"role": "user", "content": command})

            # Multi-turn tool execution loop
            while True:
                response = client.chat.completions.create(
                    model=ACTIVE_MODEL,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                if tool_calls:
                    messages.append(response_message)
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        print(f"[Executing Tool]: {function_name} with args {function_args}")
                        tool_function = available_tools.get(function_name)

                        if tool_function:
                            tool_result = tool_function(**function_args)
                            print(f"[Tool Executed Successfully]")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": str(tool_result)
                            })
                        else:
                            speak(f"Error: Tool {function_name} not found.")
                else:
                    reply = response_message.content
                    if reply:
                        cleaned_reply = clean_text_for_speech(reply)
                        speak(cleaned_reply)
                        
                        history.append({"role": "user", "content": command})
                        history.append({"role": "assistant", "content": reply})
                        save_memory(history)
                    break

        except sr.UnknownValueError:
            print("[Could not understand audio, Sir]")
            speak("I couldn't catch that, Sir. Please speak clearly.")
            break
        except Exception as e:
            print(f"[Error Encountered]: {e}")
            break


if __name__ == "__main__":
    speak("All local protocols active. Jarvis is online, Sir.")
    while True:
        if wait_for_wake_word():
            run_jarvis()


# Tool Declaration for OpenAI/Groq API style tool specs
TERMINAL_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "run_terminal_command",
        "description": "Executes shell commands silently in the background. Returns stdout, stderr, and current working directory. Use for system inspection, running scripts, and managing files.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The exact terminal command to execute."
                }
            },
            "required": ["command"]
        }
    }
}

def dispatch_tool_call(tool_call) -> dict:
    """
    Parses incoming LLM tool calls and routes them to the execution engine.
    """
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "run_terminal_command":
        cmd = arguments.get("command")
        print(f"\n[JARVIS EXEC]: {cmd}")
        
        result = terminal.execute(cmd)
        
        # Print live status feedback to developer console
        if result["status"] == "success":
            print(f"[STATUS: OK] (CWD: {result['cwd']})")
        else:
            print(f"[STATUS: {result['status'].upper()}] ERR: {result['stderr'][:100]}")

        # Package the result payload back to the model's message history
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": json.dumps(result)
        }

    return {"error": "Unknown tool called"}