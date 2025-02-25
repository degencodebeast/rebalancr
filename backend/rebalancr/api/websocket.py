from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            json_message = json.dumps(message)
            for connection in self.active_connections[user_id]:
                await connection.send_text(json_message)
                
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        json_message = json.dumps(message)
        for connections in self.active_connections.values():
            for connection in connections:
                await connection.send_text(json_message)
    
    async def broadcast_to_topic(self, topic: str, message: dict):
        """Send message to all users subscribed to a topic"""
        # This could be enhanced with a topic subscription mechanism
        # For now, a simple broadcast as placeholder
        await self.broadcast({
            "topic": topic,
            "data": message
        })

# Global connection manager instance
connection_manager = ConnectionManager()
