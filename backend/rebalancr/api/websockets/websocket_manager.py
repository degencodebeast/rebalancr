from typing import Dict, List, Any, Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        logger.info("WebSocket Manager initialized")
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}")
    
    async def disconnect(self, client_id: str):
        """Disconnect a client and remove from active connections"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client disconnected: {client_id}")
    
    async def send_personal_message(self, message: Any, websocket_id: str):
        """Send a message to a specific client"""
        if websocket_id in self.active_connections:
            websocket = self.active_connections[websocket_id]
            try:
                # Convert dict to JSON if needed
                if isinstance(message, dict):
                    await websocket.send_json(message)
                else:
                    await websocket.send_text(str(message))
            except Exception as e:
                logger.error(f"Error sending message to {websocket_id}: {str(e)}")
                # On error, try to disconnect cleanly
                await self.disconnect(websocket_id)