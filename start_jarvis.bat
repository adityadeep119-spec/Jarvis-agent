@echo off
title Jarvis Autonomous System
cd /d "C:\Users\DEEP ADITYA\jarvis_assistant"
call venv\Scripts\activate
python telegram_bridge.py
pause