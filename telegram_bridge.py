import os
import sys
import subprocess
from dotenv import load_dotenv
from voice_engine import speak
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Import Jarvis internal modules
from router import query_jarvis
from tools import open_application, get_battery_status, get_system_stats, capture_screenshot, send_whatsapp_message
from executor import execute_autonomous_task

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initial greeting command."""
    await update.message.reply_text(
        "Jarvis Remote Bridge active, Sir. I am linked to your host PC and standing by."
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reports live battery, CPU, and RAM stats to your phone."""
    battery = get_battery_status()
    stats = get_system_stats()
    report = f"--- HOST PC DIAGNOSTICS ---\n{battery}\n{stats}"
    await update.message.reply_text(report)

async def telegram_message_handler(update, context):
    user_message = update.message.text
    # Generate response...
    response_text = "Command executed successfully via remote bridge, Sir."
    
    # Speak it out loud on your local machine
    speak(response_text)
    
    # Send text back to Telegram chat
    await update.message.reply_text(response_text)


async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gives you visual eyes on your PC screen from anywhere."""
    await update.message.reply_text("Capturing desktop screenshot...")
    filename = "telegram_snap.png"
    capture_screenshot(filename)
    
    with open(filename, "rb") as photo:
        await update.message.reply_photo(photo=photo, caption="Desktop Screen Capture, Sir.")


def speak(text):
    """
    Converts text to speech locally using Piper TTS and plays it instantly on Windows.
    """
    print(f"[Jarvis Voice]: {text}")
    
    # Clean text for command line execution
    clean_text = text.replace('"', "'").replace('\n', ' ')
    
    output_audio = "response.wav"
    
    # Using Piper TTS with a clean standard English model (en_US-lessac-medium)
    command = f'echo "{clean_text}" | piper --model en_US-lessac-medium --output_file {output_audio}'
    
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Play the generated audio file natively on Windows
        if os.path.exists(output_audio):
            os.system(f"start {output_audio}")
    except Exception as e:
        print(f"[Voice Error]: Failed to synthesize speech - {str(e)}")

if __name__ == "__main__":
    # Quick test
    speak("Neural voice engine online and fully operational, Sir.")

async def exec_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggers autonomous Python code generation and execution from your phone."""
    task_prompt = " ".join(context.args)
    if not task_prompt:
        await update.message.reply_text("Please provide a task. Usage: /exec <task description>")
        return
    await update.message.reply_text(f"Executing autonomous task: '{task_prompt}'...")
    result = execute_autonomous_task(task_prompt)
    await update.message.reply_text(result)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes any standard text message through Jarvis's 3-Brain Pipeline & ChromaDB."""
    user_text = update.message.text.strip()
    text_lower = user_text.lower()

    # Strip conversational prefix if you start with "jarvis "
    if text_lower.startswith("jarvis "):
        text_lower = text_lower[7:].strip()

    # Action Trigger 1: Open/Launch Application
    action_keywords = ["open ", "launch ", "start ", "run "]
    for kw in action_keywords:
        if text_lower.startswith(kw):
            app_name = text_lower.replace(kw, "").strip()
            res = open_application(app_name)
            
            # If quick launch fails, hand over to autonomous code executor
            if "not in my quick-launch" in res:
                await update.message.reply_text(f"App not indexed. Invoking autonomous execution to launch '{app_name}' on Windows")
                res = execute_autonomous_task(f"Launch or open {app_name} on Windows")
            
            await update.message.reply_text(res)
            return

    # Action Trigger 2: Explicit Execute Request
    if text_lower.startswith("execute ") or text_lower.startswith("do "):
        task = user_text.split(" ", 1)[1]
        await update.message.reply_text(f"Executing autonomous task: '{task}'...")
        res = execute_autonomous_task(task)
        await update.message.reply_text(res)
        return

    # Action Trigger 3: Dynamic WhatsApp Automation Integration
    if text_lower.startswith("message ") or text_lower.startswith("send whatsapp to "):
        try:
            parts = text_lower.replace("send whatsapp to ", "").replace("message ", "").split(" ", 1)
            target_name = parts[0].strip()
            message_text = parts[1].strip() if len(parts) > 1 else "Hello!"
            
            send_whatsapp_message(target_name, message_text)
            await update.message.reply_text(f"Message sent to {target_name} on WhatsApp!")
        except Exception as e:
            await update.message.reply_text(f"Failed to send WhatsApp message. Error: {str(e)}")
        return

    # Fallback: General LLM Knowledge Conversation
    reply, brain = query_jarvis(user_text)
    await update.message.reply_text(f"[{brain}]: {reply}")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        print("[Error]: TELEGRAM_BOT_TOKEN is missing in your .env file!")
        sys.exit(1)

    print("--- [Telegram Remote Bridge Active] ---")
    print("Listening for incoming mobile commands...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("screenshot", screenshot_command))
    app.add_handler(CommandHandler("exec", exec_command))

    # Natural Language Router Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()