# 🤖 AI Chatbot
🌐 Live Demo: https://ai-chatbot-3fwm.onrender.com

A simple production-ready AI chatbot with FastAPI, SQLite, and OpenRouter

## 🚀 Features
- Chat with AI
- Remembers conversation (SQLite memory)
- FastAPI backend
- Real-time responses
- Deployed on Render

## 📸 Preview
<img width="1028" height="920" alt="Screenshot 2026-03-29 211657" src="https://github.com/user-attachments/assets/f0f46404-3a3c-4afb-ba5d-d85dd09dab3a" />




## Setup

```bash
cd chatbot
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Run

```bash
cd chatbot
# Windows:
set OPENAI_API_KEY=your_key_here
python -m app.main

# Or with uvicorn directly:
uvicorn app.main --reload --port 8000
```

## Endpoints

- `GET /` - Chat UI
- `POST /chat` - Send message, returns `{"response": "..."}`
- `GET /history` - Get recent messages

## Project Structure

```
chatbot/
├── app/
│   └── main.py          # FastAPI application
├── static/
│   └── index.html       # Frontend UI
├── data/                # SQLite database (created at runtime)
├── requirements.txt
├── .env.example
└── README.md
```
