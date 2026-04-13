from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from database import get_db
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

SYSTEM_PROMPT = """You are EduPath AI, a friendly and knowledgeable mentor 
helping Indian students with study abroad decisions. You help with:
- University selection for USA, UK, Canada, Germany, Australia
- Visa processes and requirements  
- Education loan guidance in India
- SOP and application tips
- Career prospects after graduation
Be concise (max 3-4 sentences), warm, and encouraging. 
Always respond in simple English that Indian students can understand."""

class ChatMessage(BaseModel):
    message: str
    student_id: int
    chat_history: Optional[List[dict]] = []

async def get_claude_response(messages: list, student_context: dict = None):
    context = f"\nStudent Profile: GPA {student_context.get('gpa')}, Target: {student_context.get('target_country')}, Course: {student_context.get('target_course')}" if student_context else ""
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": CLAUDE_API_KEY or "fallback-key-missing",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1000,
        "system": SYSTEM_PROMPT + context,
        "messages": messages
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(CLAUDE_API_URL, json=payload, headers=headers)
            data = response.json()
            if "content" in data:
                return data["content"][0]["text"]
            else:
                return f"Error from Claude: {data.get('error', 'Unknown error')}"
        except Exception as e:
            return f"System error calling AI: {str(e)}"

@router.post("/")
async def chat_with_ai(chat: ChatMessage):
    # Get user context
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (chat.student_id,))
    student = cursor.fetchone()
    student_ctx = dict(student) if student else None
    
    # Save user message to DB
    cursor.execute('INSERT INTO chat_history (student_id, role, message) VALUES (?, ?, ?)', (chat.student_id, 'user', chat.message))
    
    # Format messages for Claude
    formatted_messages = []
    for msg in chat.chat_history:
        formatted_messages.append({"role": msg["role"], "content": msg["message"]})
    formatted_messages.append({"role": "user", "content": chat.message})
    
    ai_response = await get_claude_response(formatted_messages, student_ctx)
    
    # Save bot message to DB
    cursor.execute('INSERT INTO chat_history (student_id, role, message) VALUES (?, ?, ?)', (chat.student_id, 'assistant', ai_response))
    conn.commit()
    conn.close()
    
    return {"message": ai_response}

@router.get("/history/{student_id}")
def get_chat_history(student_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT role, message FROM chat_history WHERE student_id = ? ORDER BY created_at ASC', (student_id,))
    history = cursor.fetchall()
    conn.close()
    return {"history": [dict(row) for row in history]}
