"""
FastAPI Chatbot Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import os
import sqlite3
import openai

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chat.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("MODEL", "openai/gpt-4o-mini")
MAX_MESSAGES = 20

app = FastAPI()

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_recent_messages(limit: int = MAX_MESSAGES):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.execute(
        "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def save_message(role: str, content: str):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute(
        "INSERT INTO messages (role, content, created_at) VALUES (?, ?, ?)",
        (role, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    # Keep only last MAX_MESSAGES * 2 (user + assistant pairs)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("""
        DELETE FROM messages WHERE id NOT IN (
            SELECT id FROM messages ORDER BY id DESC LIMIT ?
        )
    """, (MAX_MESSAGES * 2,))
    conn.commit()
    conn.close()


def clear_messages():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("DELETE FROM messages")
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "static", "index.html"))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    save_message("user", request.message)

    try:
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        messages.extend(get_recent_messages())

        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        assistant_message = response.choices[0].message.content
        save_message("assistant", assistant_message)

        return ChatResponse(response=assistant_message)
    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def history():
    messages = get_recent_messages(limit=MAX_MESSAGES * 2)
    return {"messages": messages}


@app.post("/clear")
async def clear():
    clear_messages()
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
