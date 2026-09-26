import os
import glob
import subprocess
import cv2
import base64
import pyautogui
from groq import Groq

groq_client = Groq()



import os

def open_application(app_name, **kwargs):
    # --- UNIVERSAL FILE INTERCEPTOR ---
    clean_input = str(app_name).strip('"\'* ')
    
    # Check if the input looks like a file name or has a file extension
    file_extensions = ['.html', '.pdf', '.docx', '.txt', '.py', '.json', '.png', '.jpg']
    is_file_like = any(clean_input.lower().endswith(ext) for ext in file_extensions) or '.' in clean_input and not ' ' in clean_input
    
    if is_file_like:
        # Automatically find and open the file using absolute path lookup
        for root, dirs, files in os.walk(r"C:\Users\DEEP ADITYA"):
            for file in files:
                if clean_input.lower() in file.lower():
                    full_path = os.path.join(root, file)
                    os.startfile(full_path)
                    return f"Successfully intercepted and opened file: {file}, Sir."
        return f"Could not find a matching file for '{clean_input}', Sir."
    # -----------------------------------
    
    # [KEEP ALL YOUR ORIGINAL APP-LAUNCHING CODE BELOW THIS]
    # ... your current app logic execution ...
    app_lower = app_name.lower()
    
    if "whatsapp" in app_lower:
        subprocess.Popen("start whatsapp:", shell=True)
        if message:
            import time
            time.sleep(3.5)
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            
            target_contact = contact if contact else "Dhruv"
            pyautogui.write(target_contact, interval=0.05)
            
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.write(message, interval=0.03)
            pyautogui.press('enter')
            return f"Successfully launched WhatsApp and sent message to {target_contact}, Sir."
            
        return f"Successfully launched WhatsApp, Sir."

    elif "telegram" in app_lower:
        subprocess.Popen("start telegram:", shell=True)
        return f"Successfully launched Telegram, Sir."
        
    elif "edge" in app_lower or "browser" in app_lower:
        subprocess.Popen("start msedge", shell=True)
        return f"Successfully launched Edge, Sir."

    paths = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\**\*.lnk",
        os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\**\*.lnk")
    ]

    launched = False
    for pattern in paths:
        for lnk in glob.glob(pattern, recursive=True):
            if app_lower in os.path.basename(lnk).lower():
                os.startfile(lnk)
                launched = True
                break
        if launched:
            break

    if not launched:
        try:
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Successfully launched {app_name}, Sir."
        except Exception as e:
            return f"Failed to launch {app_name}: {str(e)}"

def close_application(app_name: str):
    """Universally closes any running application or active window."""
    try:
        app_lower = app_name.lower().strip().replace(".exe", "")
        output = subprocess.check_output("tasklist", shell=True).decode(errors="ignore")
        
        killed_any = False
        for line in output.splitlines():
            parts = line.split()
            if parts:
                proc_name = parts[0].lower()
                if app_lower in proc_name:
                    subprocess.Popen(f"taskkill /f /im {parts[0]}", shell=True)
                    killed_any = True
                    
        if not killed_any:
            subprocess.Popen(f"taskkill /f /fi \"WINDOWTITLE eq {app_name}*\"", shell=True)
            
        return f"Successfully closed {app_name}, Sir."
    except Exception as e:
        return f"Failed to close {app_name}: {str(e)}"

import pyperclip
import pyautogui
import time
import re

def type_text(text: str, press_enter: bool = False):
    """
    Strips markdown wrappers, preserves exact raw formatting, 
    and instantly pastes heavy code blocks without typing mistakes.
    """
    try:
        clean_text = str(text)
        
        # 1. Dynamically strip markdown backticks and language tags
        clean_text = re.sub(r'```[a-zA-Z0-9_]*\n?', '', clean_text)
        clean_text = clean_text.replace('```', '')
        
        # 2. Normalize newline formatting for editors
        clean_text = clean_text.replace('\r\n', '\n').replace('\n', '\r\n').strip()
        
        # 3. Copy clean text to clipboard
        pyperclip.copy(clean_text)
        time.sleep(0.15)
        
        # 4. Trigger Ctrl+V to paste instantly
        pyautogui.hotkey('ctrl', 'v')
        
        # 5. Automatically press Enter if required
        if press_enter:
            time.sleep(0.05)
            pyautogui.press('enter')
            
        return "Successfully pasted clean text onto the active window, Sir."
        
    except Exception as e:
        return f"Failed to type text: {str(e)}"

def analyze_camera_feed(prompt: str = "What do you see in front of the camera?"):
    """Captures an image from the webcam and analyzes it using Groq's vision endpoint."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Error: Could not access the camera, Sir."
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return "Error: Failed to grab a frame from the camera, Sir."
            
        image_path = "temp_capture.jpg"
        cv2.imwrite(image_path, frame)
        
        with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
        if os.path.exists(image_path):
            os.remove(image_path)
            
        completion = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=1024  # Increased token limit so it never cuts off mid-sentence
        )
        return f"Visual Analysis: {completion.choices[0].message.content}"
    except Exception as e:
        return f"Failed to process camera feed: {str(e)}"

import GPUtil

def get_gpu_info():
    """MANDATORY TOOL: Use this function whenever the user asks about their GPU, graphics card, or graphics hardware."""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return "No dedicated GPU detected, Sir."
        
        gpu_info = []
        for i, gpu in enumerate(gpus):
            gpu_info.append(f"GPU {i}: {gpu.name} with {gpu.memoryTotal}MB VRAM (Load: {gpu.load*100:.1f}%, Temp: {gpu.temperature}°C)")
        
        return " | ".join(gpu_info)
    except Exception as e:
        return f"Failed to fetch GPU info: {str(e)}"

import os

def search_files(query: str, search_path: str = "C:\\Users"):
    """Recursively searches for any file, document, or folder by name across the system, Sir."""
    matches = []
    query_lower = query.lower()
    try:
        for root, dirs, files in os.walk(search_path):
            # Skip heavy system directories to keep search lightning fast for the demo
            if "Windows" in root or "AppData\\Local" in root:
                continue
            for name in files + dirs:
                if query_lower in name.lower():
                    matches.append(os.path.join(root, name))
                    if len(matches) >= 15:  # Cap results to ensure zero lag
                        break
            if len(matches) >= 15:
                break
        
        if matches:
            clean_matches = [m.replace("\\", "/") for m in matches]
            print(f"Debug Paths Found: {clean_matches}") # Keeps full list visible in terminal
            return f"Successfully located {len(matches)} resume files, including {os.path.basename(matches[0])} and others, Sir."

        return f"No files or folders matching '{query}' were found, Sir."
    except Exception as e:
        return f"File search failed: {str(e)}"

import os

import os

def open_file(file_query):
    """
    CRITICAL: Use this tool ONLY when the user wants to open a document, code file, 
    HTML page, PDF, or text file. Never route files to open_application.
    Accepts either an absolute path or a filename/keyword.
    """
    clean_query = str(file_query).strip('"\'* ')
    target_path = None
    
    # 1. Check if a valid direct path was provided
    if os.path.exists(clean_query):
        target_path = clean_query
    else:
        # 2. Targeted search paths (Documents, Desktop, Downloads) to prevent system freezing
        safe_directories = [
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Downloads")
        ]
        
        for search_dir in safe_directories:
            if not os.path.exists(search_dir):
                continue
            for root, dirs, files in os.walk(search_dir):
                # Skip heavy or hidden folders to keep it blazing fast
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if clean_query.lower() in file.lower() or file.lower() in clean_query:
                        target_path = os.path.join(root, file)
                        break
                if target_path:
                    break
            if target_path:
                break
                
    # 3. Execute native Windows launch
    if target_path and os.path.exists(target_path):
        try:
            normalized_path = target_path.replace("/", "\\")
            os.startfile(normalized_path)
            return f"Successfully opened {os.path.basename(normalized_path)}, Sir."
        except Exception as e:
            return f"Error launching file: {str(e)}"
    else:
        return f"Could not find or open any file matching '{file_query}', Sir."

import ctypes
import os
import platform
import subprocess
import psutil

CREATE_NO_WINDOW = 0x08000000

def get_gpu_info():
    """Fetches GPU names using PowerShell CIM (Windows 10/11 safe)."""
    # Attempt 1: PowerShell CIM query (Works on modern Windows 11)
    try:
        cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name"'
        output = subprocess.check_output(cmd, shell=True, creationflags=CREATE_NO_WINDOW, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
        gpus = [line.strip() for line in output.splitlines() if line.strip()]
        if gpus:
            return ", ".join(gpus)
    except Exception:
        pass

    # Attempt 2: WMIC Fallback for legacy builds
    try:
        output = subprocess.check_output("wmic path win32_VideoController get name", shell=True, creationflags=CREATE_NO_WINDOW, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
        gpus = [line.strip() for line in output.splitlines() if line.strip() and "Name" not in line]
        if gpus:
            return ", ".join(gpus)
    except Exception:
        pass

    return "Graphics hardware detected, model query unreadable"


def control_system(action: str = "telemetry"):
    """
    Handles Windows hardware controls and returns deep system telemetry.
    Actions: 'volume_up', 'volume_down', 'mute', 'lock_pc', 'telemetry'
    """
    action = action.lower().strip()
    
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    
    if action == "volume_up":
        for _ in range(5):
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
        return "Volume increased."
        
    elif action == "volume_down":
        for _ in range(5):
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
        return "Volume decreased."
        
    elif action == "mute":
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
        return "Audio muted."
        
    elif action == "lock_pc":
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked."
        
    elif action in ["telemetry", "system_status", "specs", "battery", "gpu", "cpu", "ram", "disk"]:
        cpu_usage = psutil.cpu_percent(interval=0.3)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_model = platform.processor() or "Unknown CPU"

        ram_info = psutil.virtual_memory()
        ram_used_gb = round(ram_info.used / (1024**3), 1)
        ram_total_gb = round(ram_info.total / (1024**3), 1)

        disk_str = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                free_gb = round(usage.free / (1024**3), 1)
                disk_str.append(f"{partition.device} ({free_gb} GB free)")
            except Exception:
                pass
        disks_summary = ", ".join(disk_str)

        bat = psutil.sensors_battery()
        bat_str = f"{bat.percent}% ({'Plugged in' if bat.power_plugged else 'On battery'})" if bat else "Desktop / Plugged in"

        gpu_str = get_gpu_info()

        return (
            f"SYSTEM TELEMETRY SUMMARY:\n"
            f"- GPU: {gpu_str}\n"
            f"- CPU: {cpu_model} ({cpu_count} logical cores) at {cpu_usage}% load\n"
            f"- RAM: {ram_used_gb} GB used / {ram_total_gb} GB total ({ram_info.percent}%)\n"
            f"- Storage: {disks_summary}\n"
            f"- Battery: {bat_str}\n"
            f"- OS: {platform.system()} {platform.release()}"
        )

    return f"Unknown action: {action}"

import webbrowser
import urllib.parse
import subprocess

def web_and_app_navigator(action: str, target: str = ""):
    """
    Safely handles web searches, YouTube queries, and local app launching. 
    Guaranteed never to kill processes or close background applications.
    """
    try:
        action = action.lower().strip()
        target = target.strip()
        
        # Local app paths dictionary (add or update your app shortcuts here)
        app_mapping = {
            "vscode": "code",
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "paint": "mspaint.exe",
            "edge": "msedge.exe",
            "chrome": "chrome.exe",
            "spotify": "spotify",
            "discord": r"C:\Users\DEEP ADITYA\AppData\Local\Discord\Update.exe --processStart Discord.exe",
            "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            "steam": r"C:\Program Files (x86)\Steam\steam.exe",
            "command prompt": "prompt"
            
        }

        # 1. YouTube Search Handling
        if "youtube" in action or action == "play_youtube":
            query = urllib.parse.quote(target)
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return f"Successfully searched YouTube for {target}, Sir."
            
        # 2. Google Search Handling
        elif "search" in action or "google" in action:
            query = urllib.parse.quote(target)
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Successfully searched Google for {target}, Sir."
            
        # 3. Opening Apps or Websites
        elif "open" in action:
            target_lower = target.lower()
            if target_lower in app_mapping:
                subprocess.Popen(app_mapping[target_lower], shell=True)
                return f"Successfully launched {target}, Sir."
            elif target.startswith("http://") or target.startswith("https://"):
                webbrowser.open(target)
                return f"Successfully opened URL: {target}, Sir."
            else:
                # Fallback to web search if it's not a local shortcut
                webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(target)}")
                return f"Opened search for {target}, Sir."
                
        else:
            query = urllib.parse.quote(target if target else action)
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Executed navigation for {target}, Sir."
            
    except Exception as e:
        return f"Navigation failed: {str(e)}"

from PIL import ImageGrab
import base64
import io
import traceback
from groq import Groq

def analyze_screen(prompt: str = "Please describe what is currently visible on my screen."):
    """
    Takes a silent screenshot of the desktop and passes it to Groq's Vision model.
    """
    try:
        # 1. Capture the screen silently
        screenshot = ImageGrab.grab()
        
        # 2. Convert image to Base64 format
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG", quality=80)
        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 3. Call the Vision API
        client = Groq() 
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # THIS WILL PRINT THE EXACT ERROR IN YOUR POWERSHELL CONSOLE
        print(f"\n[DEBUG VISION ERROR]: {traceback.format_exc()}\n")
        return f"Failed to capture or analyze the screen due to an internal error."

import pyautogui

def control_media(action: str):
    """
    Controls media playback (play, pause, next, previous) using virtual media keys.
    """
    try:
        action = action.lower()
        if "play" in action or "pause" in action:
            pyautogui.press('playpause')
            return "Toggled play/pause, Sir."
        elif "next" in action or "skip" in action:
            pyautogui.press('nexttrack')
            return "Skipped to the next track, Sir."
        elif "previous" in action or "back" in action:
            pyautogui.press('prevtrack')
            return "Went to the previous track, Sir."
        elif "stop" in action:
            pyautogui.press('stop')
            return "Stopped media playback, Sir."
        else:
            return f"Unknown media action: {action}"
    except Exception as e:
        return f"Failed to control media: {str(e)}"

import sqlite3
import os
from PIL import Image
import pyautogui
import cv2

DB_FILE = "jarvis_grandmaster_memory.db"
VISUAL_DIR = "jarvis_saved_visuals"
WEBCAM_DIR = "jarvis_webcam_snapshots"

# Ensure local directories for images exist
os.makedirs(VISUAL_DIR, exist_ok=True)
os.makedirs(WEBCAM_DIR, exist_ok=True)

def init_db():
    """Initializes the unified lightweight SQLite memory database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Run initialization on import
init_db()

def save_grandmaster_memory(category: str, content: str):
    """
    Saves important text notes, chat summaries, or user preferences to SQLite.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO long_term_memory (category, content) VALUES (?, ?)", (category, content))
        conn.commit()
        conn.close()
        return f"Text memory securely stored under [{category}], Sir."
    except Exception as e:
        return f"Failed to save text memory: {str(e)}"

def save_visual_memory(description: str, category: str = "screen_snapshot"):
    """
    Takes a live screenshot of your laptop display, saves it locally, 
    and logs its file path and description into SQLite.
    """
    try:
        screenshot = pyautogui.screenshot()
        img_count = len(os.listdir(VISUAL_DIR)) + 1
        img_path = os.path.join(VISUAL_DIR, f"screen_memory_{img_count}.png")
        screenshot.save(img_path)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO long_term_memory (category, content) VALUES (?, ?)", 
            (category, f"[Screen Snapshot Path: {img_path}] - Context: {description}")
        )
        conn.commit()
        conn.close()
        
        return f"Screen snapshot captured, saved locally at {img_path}, and logged to memory, Sir."
    except Exception as e:
        return f"Failed to save screen memory: {str(e)}"

def remember_webcam_capture(description: str, category: str = "webcam_snapshot"):
    """
    Captures a frame from your laptop camera, saves it locally, 
    and logs its file path and description into SQLite.
    """
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return "Failed to grab frame from laptop camera, Sir."
            
        img_count = len(os.listdir(WEBCAM_DIR)) + 1
        img_path = os.path.join(WEBCAM_DIR, f"webcam_memory_{img_count}.png")
        cv2.imwrite(img_path, frame)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO long_term_memory (category, content) VALUES (?, ?)", 
            (category, f"[Webcam Image Path: {img_path}] - Context: {description}")
        )
        conn.commit()
        conn.close()
        
        return f"Webcam frame captured, saved locally at {img_path}, and logged to memory, Sir."
    except Exception as e:
        return f"Failed to save webcam memory: {str(e)}"

def search_grandmaster_memory(keyword: str):
    """
    Searches text notes, screen captures, and webcam logs instantly 
    using a keyword without choking the token window.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT category, content FROM long_term_memory WHERE content LIKE ? OR category LIKE ?", 
                       (f"%{keyword}%", f"%{keyword}%"))
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return f"No records found matching '{keyword}' in long-term storage, Sir."
            
        formatted_results = [f"[{cat}]: {cont}" for cat, cont in results]
        return "Relevant historical memories found:\n" + "\n".join(formatted_results)
    except Exception as e:
        return f"Memory search failed: {str(e)}"


import subprocess

def set_wifi_state(state: str):
    """Turns Wi-Fi interface 'enable' or 'disable'."""
    action = "enable" if state.lower() in ["on", "enable", "true"] else "disable"
    cmd = f'Set-NetAdapter -Name "Wi-Fi" -Confirm:$false -Enabled ${"true" if action == "enable" else "false"}'
    
    # Run via PowerShell (Note: Requires PowerShell/Terminal run as Admin for adapter changes)
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
    if result.returncode == 0:
        return f"Wi-Fi has been {action}d successfully."
    else:
        # Fallback to netsh
        netsh_cmd = f'netsh interface set interface "Wi-Fi" admin={action}'
        subprocess.run(netsh_cmd, shell=True)
        return f"Issued command to turn Wi-Fi {action}."


def manage_vpn(action: str = "connect", vpn_name: str = "FastestVPN"):
    """
    Connects or disconnects a Windows VPN.
    Works with native Windows VPN profiles (rasdial) or PowerShell.
    """
    if action.lower() in ["connect", "on", "start"]:
        # Uses Windows built-in VPN client via rasdial (or PowerShell Connect-VpnConnection)
        cmd = f'Connect-VpnConnection -Name "{vpn_name}"'
        res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        if res.returncode == 0:
            return f"Successfully connected to VPN: {vpn_name}"
        else:
            # Direct rasdial fallback (rasdial "VPN_NAME" username password)
            ras = subprocess.run(f'rasdial "{vpn_name}"', shell=True, capture_output=True, text=True)
            return f"VPN Connection status: {ras.stdout.strip() or 'Attempted connection.'}"
    else:
        cmd = f'Disconnect-VpnConnection -Name "{vpn_name}"'
        subprocess.run(["powershell", "-Command", cmd], capture_output=True)
        subprocess.run(f'rasdial "{vpn_name}" /disconnect', shell=True)
        return f"Disconnected from VPN: {vpn_name}."


def set_brightness(level: int):
    """Sets monitor brightness (0 to 100%)."""
    level = max(0, min(100, level))
    cmd = f'(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})'
    subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return f"Screen brightness set to {level}%."


def set_master_volume(level: int):
    """Sets master output volume (0 to 100%)."""
    # Uses a quick PowerShell audio trigger via nircmd or direct WScript key loops
    # For precise percentage control without third-party tools:
    level = max(0, min(100, level))
    ps_cmd = f'''
    $obj = New-Object -ComObject WScript.Shell
    1..50 | % {{ $obj.SendKeys([char]174) }} # Mute down to 0
    1..{int(level/2)} | % {{ $obj.SendKeys([char]175) }} # Step up to target
    '''
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
    return f"Master volume adjusted to roughly {level}%."

import subprocess
import threading
import time

def create_desktop_reminder(message: str, delay_seconds: int = 0):
    """
    Sends a native Windows Toast notification banner AND speaks 
    the reminder out loud through Piper TTS after the delay.
    """
    def _execute_reminder():
        if delay_seconds > 0:
            time.sleep(delay_seconds)
            
        # 1. Pop up native Windows Toast Banner
        ps_toast = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $toastXml = [xml]$template.GetXml()
        $toastXml.GetElementsByTagName("text")[0].AppendChild($toastXml.CreateTextNode("Jarvis Assistant")) | Out-Null
        $toastXml.GetElementsByTagName("text")[1].AppendChild($toastXml.CreateTextNode("{message}")) | Out-Null
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($toastXml.OuterXml)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Jarvis").Show($toast)
        '''
        subprocess.run(["powershell", "-Command", ps_toast], capture_output=True)

        # 2. Speak out loud through Piper TTS
        try:
            from assistant import speak
            speak(f"Sir, here is your reminder: {message}")
        except ImportError:
            # Fallback if speak function is in a separate TTS module
            pass

    threading.Thread(target=_execute_reminder, daemon=True).start()
    
    if delay_seconds > 0:
        return f"Reminder set for {delay_seconds} seconds from now."
    return f"Displaying reminder: '{message}'."

# terminal_engine.py
import os
import re
import subprocess
import sys
from typing import Dict, Any

class TerminalEngine:
    """
    Production-grade background execution engine for Jarvis.
    Handles headless command execution, stateful working directory tracking,
    output truncation, and safety guardrail checks.
    """

    def __init__(self, initial_dir: str = None, timeout: int = 45, max_output_chars: int = 4000):
        self.working_dir = os.path.abspath(initial_dir or os.getcwd())
        self.timeout = timeout
        self.max_output_chars = max_output_chars

        # Safety Guardrails: Prevent unintended system destruction
        self.blocked_patterns = [
            r"\brm\s+-rf\s+(/|~\b|\*|\.\.)",   # Destructive root/home/parent deletes
            r"\bformat\b",                     # Disk format
            r"\bdiskpart\b",                   # Partition management
            r"\bdel\s+/[s|q|f|a]+\b",          # Recursive force deletes
            r"\brmdir\s+/s\b",                 # Directory wipes
            r"\bshutdown\b",                   # System power control
            r"\breboot\b",                     # System restart
            r":\(\){\s*:\|:&\s*};:",           # Fork bomb
            r"\bdd\s+if=",                     # Direct drive overwrites
            r"\bmkfs\b",                       # Filesystem formatting
            r"\breg\s+delete\b"                # Registry destruction
        ]

    def _verify_safety(self, command: str) -> tuple[bool, str]:
        for pattern in self.blocked_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Command execution blocked by guardrail pattern: '{pattern}'"
        return True, ""

    def _handle_cd(self, command: str) -> Dict[str, Any] | None:
        """Handles directory changes locally to persist state across tool calls."""
        cmd_strip = command.strip()
        if cmd_strip.startswith("cd ") or cmd_strip == "cd":
            target = cmd_strip[3:].strip() if len(cmd_strip) > 2 else os.path.expanduser("~")
            # Handle quoted paths
            target = target.strip('"\'')
            new_path = os.path.abspath(os.path.join(self.working_dir, target))

            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.working_dir = new_path
                return {
                    "status": "success",
                    "stdout": f"Changed working directory to: {self.working_dir}",
                    "stderr": "",
                    "returncode": 0,
                    "cwd": self.working_dir
                }
            else:
                return {
                    "status": "failed",
                    "stdout": "",
                    "stderr": f"Directory not found: {new_path}",
                    "returncode": 1,
                    "cwd": self.working_dir
                }
        return None

    def execute(self, command: str) -> Dict[str, Any]:
        """Executes a command headlessly in the active working directory."""
        # 1. Safety check
        is_safe, reason = self._verify_safety(command)
        if not is_safe:
            return {
                "status": "blocked",
                "stdout": "",
                "stderr": reason,
                "returncode": -1,
                "cwd": self.working_dir
            }

        # 2. Stateful directory handling
        cd_result = self._handle_cd(command)
        if cd_result:
            return cd_result

        # 3. Headless process execution
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        try:
            process = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                creationflags=creation_flags
            )

            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            # Truncate output if too long to save LLM context window limits
            if len(stdout) > self.max_output_chars:
                stdout = stdout[:self.max_output_chars] + f"\n... [Output truncated at {self.max_output_chars} characters]"
            if len(stderr) > self.max_output_chars:
                stderr = stderr[:self.max_output_chars] + f"\n... [Error output truncated at {self.max_output_chars} characters]"

            return {
                "status": "success" if process.returncode == 0 else "failed",
                "stdout": stdout,
                "stderr": stderr,
                "returncode": process.returncode,
                "cwd": self.working_dir
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout} seconds.",
                "returncode": -1,
                "cwd": self.working_dir
            }
        except Exception as e:
            return {
                "status": "exception",
                "stdout": "",
                "stderr": f"System error executing command: {str(e)}",
                "returncode": -1,
                "cwd": self.working_dir
            }