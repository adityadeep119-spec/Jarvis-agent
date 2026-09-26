# test_runner.py
from jarvis_tools import TerminalEngine

engine = TerminalEngine()

# Step 1: Deliberate bad command execution
cmd_step_1 = "python -c \"import non_existent_module\""
print(f"Step 1 - Running: {cmd_step_1}")
res1 = engine.execute(cmd_step_1)
print(f"Execution Output:\nSTDERR: {res1['stderr']}\n")

# Step 2: Agent reads error, corrects logic, and re-executes automatically
if res1["status"] != "success":
    print("Agent detected error! Auto-correcting payload...")
    cmd_step_2 = "python -c \"import sys; print('System Python Version:', sys.version)\""
    print(f"Step 2 - Running Corrected Command: {cmd_step_2}")
    res2 = engine.execute(cmd_step_2)
    print(f"Execution Output:\nSTDOUT: {res2['stdout']}")