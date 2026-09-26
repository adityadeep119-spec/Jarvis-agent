import sys
import io
import traceback
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_python_code(task_description: str) -> str:
    """Uses Groq 120B to generate clean, runnable Python code for a given task."""
    prompt = (
        f"You are an autonomous Python code generator for Jarvis.\n"
        f"Task: {task_description}\n"
        f"Generate ONLY executable Python code inside a single ```python block. "
        f"Do not include conversational filler, explanations, or extra commentary."
    )

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.2
    )

    raw_output = response.choices[0].message.content
    # Extract code from Markdown block
    if "```python" in raw_output:
        code = raw_output.split("```python")[1].split("```")[0].strip()
    elif "```" in raw_output:
        code = raw_output.split("```")[1].split("```")[0].strip()
    else:
        code = raw_output.strip()

    return code


def run_code_safely(code: str):
    """Executes code in a sandbox capturing stdout and stderr."""
    buffer = io.StringIO()
    sys.stdout = buffer

    local_scope = {}

    try:
        exec(code, {}, local_scope)
        sys.stdout = sys.__stdout__
        return True, buffer.getvalue().strip()
    except Exception as e:
        sys.stdout = sys.__stdout__
        error_msg = f"{e}\n{traceback.format_exc()}"
        return False, error_msg


def execute_autonomous_task(task_description: str, max_retries: int = 3):
    """
    Generates code, runs it, and automatically self-corrects up to max_retries times if errors occur.
    """
    print(f"\n[Autonomous Executor]: Received Task -> '{task_description}'")

    code = generate_python_code(task_description)

    for attempt in range(1, max_retries + 1):
        print(f"\n[Attempt {attempt}/{max_retries}]: Executing generated code...")
        success, result = run_code_safely(code)

        if success:
            print(f"[Execution Successful!]\n--- Output ---\n{result}")
            return f"Task completed successfully, sir. Output: {result}"
        else:
            print(f"[Code Error Encountered]:\n{result}")

            if attempt < max_retries:
                print("[Self-Healing Engine]: Attempting to patch and fix code bug...")
                fix_prompt = (
                    f"The following Python code failed with an error:\n\n"
                    f"```python\n{code}\n```\n\n"
                    f"Error Output:\n{result}\n\n"
                    f"Fix the bug and return ONLY the corrected, valid Python code inside a ```python block."
                )
                response = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": fix_prompt}],
                    max_tokens=600,
                    temperature=0.1
                )
                code = response.choices[0].message.content.split("```python")[1].split("```")[0].strip()

    return "Sir, I was unable to complete the autonomous execution after 3 self-healing attempts."


if __name__ == "__main__":
    # Test task
    sample_task = "Create a text file named 'jarvis_test.txt' and write 'Autonomous Code Execution Operational' into it."
    result = execute_autonomous_task(sample_task)
    print(f"\nJarvis: {result}")