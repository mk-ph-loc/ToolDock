@echo off
if exist .venv\Scripts\python.exe (.venv\Scripts\python.exe -m tooldock) else (python -m tooldock)
