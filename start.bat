@echo off
cd /d "%~dp0"
uvicorn app.main:app --host 0.0.0.0 --port 10000 --env-file .env --reload
