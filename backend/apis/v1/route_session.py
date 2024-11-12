# apis/v1/route_session.py
from fastapi import APIRouter, WebSocket, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Optional
from datetime import datetime
import json

router = APIRouter()

from bot.database_manager import DatabaseManager

class YouTubeSessionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.db = DatabaseManager()

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def store_session(self, user_id: str, auth_data: dict):
        # Store session in your database
        await self.db.execute(
            """
            INSERT INTO youtube_sessions (user_id, auth_data, created_at, last_used)
            VALUES (:user_id, :auth_data, :created_at, :last_used)
            ON CONFLICT (user_id) 
            DO UPDATE SET auth_data = :auth_data, last_used = :last_used
            """,
            {
                "user_id": user_id,
                "auth_data": json.dumps(auth_data),
                "created_at": datetime.utcnow(),
                "last_used": datetime.utcnow()
            }
        )

session_manager = YouTubeSessionManager()

@router.websocket("/ws/youtube-login/{user_id}")
async def youtube_login_websocket(websocket: WebSocket, user_id: str):
    await session_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "youtube_session":
                # Store the session data
                await session_manager.store_session(user_id, data["authData"])
                # Send confirmation back to client
                await websocket.send_json({
                    "type": "session_stored",
                    "success": True
                })
            elif data["type"] == "logout":
                # Handle logout
                await session_manager.db.execute(
                    "DELETE FROM youtube_sessions WHERE user_id = :user_id",
                    {"user_id": user_id}
                )
    except Exception as e:
        print(f"Error in websocket connection: {e}")
    finally:
        await session_manager.disconnect(user_id)

@router.get("/youtube/session/{user_id}")
async def get_youtube_session(user_id: str):
    session = await session_manager.db.fetch_one(
        "SELECT auth_data FROM youtube_sessions WHERE user_id = :user_id",
        {"user_id": user_id}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse(content=json.loads(session["auth_data"]))

@router.post("/validate-youtube-session")
async def validate_youtube_session(auth_data: dict):
    # Implement your session validation logic here
    # This could involve checking with YouTube's API
    try:
        # Example validation (you should implement proper validation)
        if auth_data:  # Replace with actual validation
            return JSONResponse(content={"valid": True})
        return JSONResponse(content={"valid": False})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))