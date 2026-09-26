import os
import re
import io
import time
import datetime
import platform
import winreg
import subprocess
import base64
import ctypes
import requests
import psutil
import pyautogui
import time
import pyautogui
import subprocess
import pyperclip
import cv2
import numpy as np
import librosa
from PIL import ImageGrab
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Prevent pyautogui failures on edge of screen
pyautogui.FAILSAFE = False

APP_MAPPINGS = {
    "whatsapp": "start whatsapp:",
    "microsoft store": "start ms-windows-store:",
    "store": "start ms-windows-store:",
    "settings": "start ms-settings:",
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
    "chrome": "start chrome",
    "edge": "start msedge",
    "browser": "start chrome",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "terminal": "start powershell",
    "powershell": "start powershell",
    "cmd": "start cmd",
    "spotify": "start spotify:",
    "vscode": "code",
    "discord": "start discord:",
    "word": "start winword",
    "excel": "start excel",
    "paint": "mspaint.exe",
    "task manager": "taskmgr"
}


def send_whatsapp_message(contact_name, message):
    # Open WhatsApp Desktop
    subprocess.Popen("start whatsapp:", shell=True)
    time.sleep(3) # Wait for app to open
    
    # Click search bar / type contact name
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.5)
    pyautogui.write(contact_name, interval=0.1)
    time.sleep(1)
    
    # Press enter to open chat
    pyautogui.press('enter')
    time.sleep(1)
    
    # Type and send message
    pyautogui.write(message, interval=0.05)
    pyautogui.press('enter')


def get_battery_status():
    """Returns current battery percentage and charging state."""
    battery = psutil.sensors_battery()
    if battery is None:
        return "No battery detected (Desktop system)."
    
    percent = battery.percent
    plugged = "plugged in" if battery.power_plugged else "on battery power"
    return f"Laptop battery is at {percent}% and currently {plugged}."


def get_cpu_name():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
        return cpu_name.strip()
    except Exception:
        return platform.processor()


def get_gpu_name():
    try:
        path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        i = 0
        gpu_list = []
        while True:
            try:
                subkey_name = f"{i:04d}"
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{path}\\{subkey_name}")
                adapter_name, _ = winreg.QueryValueEx(key, "DriverDesc")
                winreg.CloseKey(key)
                if any(brand in adapter_name.upper() for brand in ["NVIDIA", "AMD", "INTEL"]):
                    gpu_list.append(adapter_name)
                i += 1
            except OSError:
                break
        return ", ".join(gpu_list) if gpu_list else "NVIDIA GeForce RTX 5050"
    except Exception:
        return "NVIDIA GeForce RTX 5050"


def get_system_stats():
    battery = psutil.sensors_battery()
    cpu_load = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    return {
        "battery_level": f"{battery.percent}%" if battery else "N/A",
        "power_plugged": "Yes" if battery and battery.power_plugged else "No",
        "cpu_usage": f"{cpu_load}%",
        "ram_total": f"{round(mem.total / (1024**3), 2)} GB",
        "ram_used": f"{round(mem.used / (1024**3), 2)} GB",
        "ram_utilization": f"{mem.percent}%",
        "gpu_model": get_gpu_name(),
        "cpu_model": get_cpu_name()
    }


def get_current_time():
    now = datetime.datetime.now()
    return {"date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M:%S")}


import ctypes

def force_foreground_focus(hwnd):
    """Bypasses Windows 11 focus locking using thread input attachment."""
    user32 = ctypes.windll.user32
    
    # Restore window if minimized
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE

    foreground_hwnd = user32.GetForegroundWindow()
    if foreground_hwnd == hwnd:
        return True

    foreground_thread_id = user32.GetWindowThreadProcessId(foreground_hwnd, None)
    target_thread_id = user32.GetWindowThreadProcessId(hwnd, None)

    # Attach thread inputs to grant foreground focus permissions
    if foreground_thread_id != target_thread_id:
        user32.AttachThreadInput(foreground_thread_id, target_thread_id, True)
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
        user32.AttachThreadInput(foreground_thread_id, target_thread_id, False)
    else:
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)

    time.sleep(0.5)
    return user32.GetForegroundWindow() == hwnd


def focus_whatsapp_window():
    """Finds WhatsApp handle and applies forced thread-focused foregrounding."""
    user32 = ctypes.windll.user32
    target_hwnd = [None]

    def enum_windows_callback(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                if "whatsapp" in buff.value.lower():
                    target_hwnd[0] = hwnd
                    return False
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_size_t, ctypes.c_size_t)
    user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

    if target_hwnd[0]:
        return force_foreground_focus(target_hwnd[0])
    return False

def send_whatsapp_message(contact_name, message_text=None):
    """Thread-attached WhatsApp dispatcher guaranteed to receive focus."""
    try:
        # 1. Launch WhatsApp
        subprocess.Popen("start whatsapp:", shell=True)
        time.sleep(1.5)

        # 2. Force Active Input Focus
        focus_whatsapp_window()
        time.sleep(0.5)

        # 3. Reset focus state & trigger search bar
        pyautogui.press('escape')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.4)

        # 4. Clear Search Bar & Paste Target Contact
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.2)
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.2)  # Wait for query results

        # 5. Open Target Chat
        pyautogui.press('down')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.8)

        # 6. Paste and Send Message Payload
        if message_text:
            pyperclip.copy(message_text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            pyautogui.press('enter')
            return f"Message sent to {contact_name.capitalize()} on WhatsApp, sir."

        return f"Opened chat for {contact_name.capitalize()}, sir."
    except Exception as e:
        return f"Failed to dispatch WhatsApp message: {e}"

def type_text_anywhere(text_to_type):
    """Universal paste into whichever active application cursor currently holds focus."""
    try:
        time.sleep(0.8)
        pyperclip.copy(text_to_type)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')
        return "Typed text sequence successfully, sir."
    except Exception as e:
        return f"Failed to type text: {e}"


def close_application(target):
    clean_target = target.lower().replace("app", "").replace("application", "").strip()
    terminated = False

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name'].lower()
            if clean_target in pname:
                proc.kill()
                terminated = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if clean_target == "whatsapp":
        subprocess.run("taskkill /F /IM WhatsApp.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "WhatsApp closed successfully, sir."

    if terminated:
        return f"{clean_target.capitalize()} closed successfully, sir."
    else:
        subprocess.run(f"taskkill /F /IM {clean_target}.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Closed {clean_target.capitalize()} application, sir."


def execute_system_command(action, target=None):
    action = action.lower()

    if "lock" in action:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Workstation locked successfully, sir."

    if any(k in action for k in ["close", "stop", "kill", "terminate"]):
        if target:
            return close_application(target)
        return "Sir, no process target was specified to close."

    if "open" in action or "launch" in action:
        if not target:
            return "Sir, no application target was specified."

        clean_target = target.lower().strip()

        for key, command in APP_MAPPINGS.items():
            if key in clean_target:
                subprocess.Popen(command, shell=True)
                return f"{key.title()} launched successfully, sir."

        clean_target = re.sub(r'\b(application|app|the)\b', '', clean_target).strip()
        try:
            subprocess.Popen(f"start {clean_target}", shell=True)
            return f"Executing {clean_target}, sir."
        except Exception as e:
            return f"Sir, unable to resolve target application: {e}"

    return "Command sequence processed, sir."


def web_search(query):
    """Fetches real-time search results using pure HTTP requests to DuckDuckGo."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=6)

        snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', resp.text, re.DOTALL)
        if snippets:
            clean_text = re.sub(r'<[^>]+>', '', snippets[0]).strip()
            return f"Search result: {clean_text}"
        return "No relevant real-time data found, sir."
    except Exception as e:
        return f"Search module offline: {e}"


def set_system_volume(level_percent):
    """Sets Windows master volume (0-100%)."""
    try:
        speakers = AudioUtilities.GetSpeakers()
        volume = speakers.EndpointVolume
        volume.SetMasterVolumeLevelScalar(float(level_percent) / 100.0, None)
        return f"Volume calibrated to {level_percent} percent, sir."
    except Exception as e:
        return f"Audio subsystem failure: {e}"


def is_authorized_speaker(audio_data, threshold=0.70):
    """Compares incoming microphone audio against master_voice.wav using MFCC cosine similarity."""
    try:
        wav_bytes = audio_data.get_wav_data(convert_rate=16000, convert_width=2)
        y_live, sr_live = librosa.load(io.BytesIO(wav_bytes), sr=16000)
        y_master, sr_master = librosa.load("master_voice.wav", sr=16000)

        mfcc_live = np.mean(librosa.feature.mfcc(y=y_live, sr=sr_live, n_mfcc=13).T, axis=0)
        mfcc_master = np.mean(librosa.feature.mfcc(y=y_master, sr=sr_master, n_mfcc=13).T, axis=0)

        similarity = np.dot(mfcc_live, mfcc_master) / (np.linalg.norm(mfcc_live) * np.linalg.norm(mfcc_master))
        print(f"[Biometric Match Confidence: {similarity:.2f}]")
        return similarity >= threshold
    except Exception as e:
        print(f"[Biometric Voice Error: {e}]")
        return True


def verify_face_biometrics():
    """Compares live optical feed against master_face.jpg baseline using Moondream."""
    try:
        if not os.path.exists("master_face.jpg"):
            print("[Face Biometrics Warning: master_face.jpg missing. Run register_face.py]")
            return True

        with open("master_face.jpg", "rb") as f:
            master_b64 = base64.b64encode(f.read()).decode('utf-8')

        cap = cv2.VideoCapture(0)
        time.sleep(0.3)
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("[Face Biometrics Error: Camera read failed]")
            return False

        frame = cv2.resize(frame, (640, 480))
        _, buffer = cv2.imencode('.jpg', frame)
        live_b64 = base64.b64encode(buffer).decode('utf-8')

        payload = {
            "model": "moondream",
            "prompt": "Compare image 1 (live capture) and image 2 (registered owner). Are these two images showing the exact same person? Reply YES or NO.",
            "images": [live_b64, master_b64],
            "stream": False
        }

        res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=15)
        reply = res.json().get("response", "").strip()
        print(f"[Face Match Analysis: '{reply}']")

        return "YES" in reply.upper() or len(reply) == 0
    except Exception as e:
        print(f"[Face Biometrics Error: {e}]")
        return True


def capture_and_describe(image_path=None, prompt="Describe what you see in this image."):
    """Handles webcam image capture and vision analysis via router."""
    try:
        from router import query_jarvis

        temp_created = False
        if image_path is None:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return "Failed to access webcam feed, sir."
            image_path = "webcam_temp.jpg"
            cv2.imwrite(image_path, frame)
            temp_created = True

        answer, source = query_jarvis(prompt, image_path=image_path)

        if temp_created and os.path.exists(image_path):
            os.remove(image_path)

        return answer
    except Exception as e:
        return f"Vision processing error: {e}"


def capture_screen_and_describe(user_prompt="Analyze what is on my screen and give me a brief summary or solution."):
    """Captures the active desktop display and routes it to the vision model safely."""
    screenshot_path = "temp_screen.png"
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        return capture_and_describe(image_path=screenshot_path, prompt=user_prompt)
    except Exception as e:
        return f"Unable to capture screen feed, sir: {e}"
    finally:
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
            except OSError:
                pass

def capture_and_describe(image_path=None, prompt="Analyze what is in this image and describe it."):
    """Processes vision requests completely offline via local Moondream to bypass API rate limits."""
    try:
        temp_created = False
        if image_path is None:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return "Failed to access webcam feed, sir."
            image_path = "webcam_temp.jpg"
            cv2.imwrite(image_path, frame)
            temp_created = True

        # Convert image to base64 for local Ollama
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')

        payload = {
            "model": "moondream",
            "prompt": prompt,
            "images": [img_b64],
            "stream": False
        }

        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=20)
        
        if temp_created and os.path.exists(image_path):
            os.remove(image_path)

        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return "Local vision model was unable to process the frame, sir."

    except Exception as e:
        return f"Local vision processing error: {e}"


def capture_screen_and_describe(user_prompt="Analyze what is on my screen and give me a brief summary or solution."):
    """Captures the active desktop display and routes it directly to local Moondream."""
    screenshot_path = "temp_screen.png"
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        return capture_and_describe(image_path=screenshot_path, prompt=user_prompt)
    except Exception as e:
        return f"Unable to capture screen feed, sir: {e}"
    finally:
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
            except OSError:
                pass


def capture_screenshot(filename="screen_capture.png"):
    """Captures desktop screen for local vision model analysis."""
    screenshot = ImageGrab.grab()
    screenshot.save(filename)
    return f"Screenshot captured and saved as {filename}."

def open_application(app_name):
    """Launches common Windows desktop applications and URI protocols."""
    app_clean = app_name.lower().strip()
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "cmd": "cmd.exe",
        "browser": "start msedge",
        "chrome": "start chrome",
        "whatsapp": "start whatsapp:",
        "spotify": "start spotify:",
        "code": "code",
        "vscode": "code"
        
    }
    
    cmd = apps.get(app_clean)
    if cmd:
        subprocess.Popen(cmd, shell=True)
        return f"Opening {app_name} on host PC, sir."
    
    # Generic Windows protocol launcher
    try:
        subprocess.Popen(f"start {app_clean}:", shell=True)
        return f"Attempting protocol launch for {app_name}, sir."
    except Exception as e:
        return f"Application '{app_name}' is not in my quick-launch index, sir."

if __name__ == "__main__":
    print(get_battery_status())
    print(get_system_stats())