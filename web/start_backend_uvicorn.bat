@echo off
echo Starting MOSDAC Chatbot Backend with Uvicorn...
cd /d "c:\Users\abhis\Desktop\modac-chatbot-scraper\web"
C:/Users/abhis/Desktop/modac-chatbot-scraper/venv/Scripts/uvicorn.exe api:app --host 0.0.0.0 --port 8000 --reload
pause
