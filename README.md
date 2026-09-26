# Jarvis-agent
Autonomous system assistant built with TrueForge for Agents That Act Hackathon
# 🤖 JARVIS — Autonomous System & Infrastructure Agent

> **Theme:** Agents That Act  
> **Problem Statement:** Runbook Executor / System Administration  
> **Harness:** TrueForge (`@truefoundry/trueforge`)  

---

## 📌 Executive Summary

**JARVIS** is an autonomous, context-aware developer and infrastructure assistant designed to bridge the gap between natural language intent and safe system execution. Unlike passive chat models that merely output code snippets, JARVIS uses the **TrueForge** agent harness to safely perform real-world actions—executing scripts, running operational runbooks, and managing cloud environments with strict human-in-the-loop safeguards.

---

## 🚀 Key Features

* **🗣️ Natural Language Command Execution:** Translates complex developer/DevOps intents into structured terminal commands and workflows.
* **🛡️ Sandboxed Safety (TrueForge Integration):** Runs code execution and tool calls inside isolated sandboxes via the TrueForge harness to prevent unintended side effects on host systems.
* **⚠️ Human-in-the-Loop Verification:** Automatically pauses and prompts for developer confirmation before executing destructive, high-risk, or irreversible system operations.
* **⚡ Ultra-Fast Inference:** Leverages high-throughput model endpoints (e.g., Groq / OpenAI) for near-instant reasoning and plan generation.
* **📊 Live Feedback Loop:** Streams execution stdout/stderr logs and state changes directly back to the interface in real time.

---

## 🛠️ Tech Stack & Architecture

* **Agent Harness:** [TrueForge](https://github.com/truefoundry/trueforge) (MIT Licensed)
* **LLM Engine:** Groq / OpenAI / Compatible Open-Source API
* **Language/Runtime:** Node.js / Python
* **Tooling:** VS Code, Cursor, GitHub Copilot

---

## 💡 How It Works (End-to-End Workflow)

1. **User Request:** The user provides a natural language task (e.g., *"Perform system check, clean unused docker caches, and inspect high-memory processes"*).
2. **Planning & Tool Selection:** JARVIS parses the intent, breaks it down into deterministic shell commands/tools, and submits the plan to TrueForge.
3. **Sandboxed Execution:** TrueForge spins up an isolated sandbox environment and executes the commands.
4. **Interactive Approval:** If an action touches critical system state, JARVIS halts and waits for explicit user confirmation.
5. **Output Summarization:** Real-time log outputs are captured, evaluated, and presented back to the user as a concise run report.

---

## ⚡ Quickstart & Local Setup

### 1. Prerequisites
Ensure you have Node.js (v18+) and Git installed.

### 2. Clone the Repository
```bash
git clone [https://github.com/adityadeep119-spec/Jarvis-agent.git](https://github.com/adityadeep119-spec/Jarvis-agent.git)
cd Jarvis-agent
