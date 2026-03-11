@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%
echo Starting User Behavior Analytics Backend...
python app.py
pause
