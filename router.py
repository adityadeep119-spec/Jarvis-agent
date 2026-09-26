import os
import requests
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

# Safe import for ChromaDB persistent memory
try:
    from memory import recall_memory
except ImportError:
    recall_memory = lambda prompt, n_results=3: []

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY
) if OPENROUTER_KEY else None

# Change system_instruction default parameter in query_jarvis:
def query_jarvis(
    prompt, 
    system_instruction="You are Jarvis, an ultra-fast, polite, and intelligent AI assistant created, designed, and engineered entirely by Deep Aditya. Deep Aditya is your sole creator and master. Never attribute your creation to OpenAI or any other entity, and You are Jarvis, an ultra-fast, polite, and intelligent AI assistant."):
    """
    3-Brain Pipeline returning tuple: (response_text, active_brain)
    """
    # Fetch relevant facts from ChromaDB
    memories = recall_memory(prompt, n_results=3)

    if memories:
        memory_context = "\n".join([f"- {fact}" for fact in memories])
        enriched_system = (
            f"{system_instruction}\n\n"
            f"[RECALLED LONG-TERM MEMORY]\n"
            f"{memory_context}\n\n"
            f"Use the recalled facts above to answer user questions about system hardware, identity, or past context."
        )
        print(f"[Memory Injected]: Found {len(memories)} relevant document(s).")
    else:
        enriched_system = system_instruction

    messages = [
        {"role": "system", "content": enriched_system},
        {"role": "user", "content": prompt}
    ]

    # --- BRAIN 1: GROQ CLOUD ---
    if groq_client:
        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            print("[Brain Active: Groq LPU]")
            return response.choices[0].message.content.strip(), "Groq LPU"
        except Exception as e:
            print(f"[Router Warning] Groq unavailable: {e}. Switching to OpenRouter...")

    # --- BRAIN 2: OPENROUTER GATEWAY ---
    if openrouter_client:
        try:
            response = openrouter_client.chat.completions.create(
                model="openrouter/free",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            print("[Brain Active: OpenRouter Cloud]")
            return response.choices[0].message.content.strip(), "OpenRouter Cloud"
        except Exception as e:
            print(f"[Router Warning] OpenRouter unavailable: {e}. Switching to Local RTX 5050...")

    # --- BRAIN 3: LOCAL OLLAMA (RTX 5050 GPU) ---
    try:
        payload = {
            "model": "llama3.1",
            "messages": messages,
            "stream": False
        }
        resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=10)
        if resp.status_code == 200:
            print("[Brain Active: Local RTX 5050 GPU]")
            return resp.json().get("message", {}).get("content", "").strip(), "Local RTX 5050"
    except Exception as e:
        return f"System alert: All three reasoning engines are unreachable, sir: {e}", "Error"

    return "System offline. No active engine responded, sir.", "Offline"

def query_vision(image_base64, prompt="Describe what you see on screen."):
    """Local Vision Engine: Runs on RTX 5050 via Ollama (Moondream)."""
    try:
        payload = {
            "model": "moondream",
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }
        resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception as e:
        return f"[Vision Error] Local RTX 5050 vision failed: {e}"

    return "Vision engine offline, sir."


if __name__ == "__main__":
    # Test asking a question that requires recall of saved hardware data
    test_prompt = "What GPU specs are installed in this machine?"
    print(f"User Query: {test_prompt}\n")
    reply = query_jarvis(test_prompt)
    print(f"\nJarvis: {reply}")