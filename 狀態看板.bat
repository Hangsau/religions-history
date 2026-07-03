@echo off
rem 雙擊開啟 religions-history 狀態看板（刊版）。pythonw = 無主控台視窗。
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
start "" pythonw "%~dp0scripts\status_gui.py"
