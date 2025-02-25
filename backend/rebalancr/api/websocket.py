from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json

class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Store topic subscriptions by user_id
        self.topic_subscriptions: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        
        # Initialize user connections if not exists
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            self.topic_subscriptions[user_id] = set()
            
        self.active_connections[user_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Clean up topic subscriptions when all connections are closed
                if user_id in self.topic_subscriptions:
                    del self.topic_subscriptions[user_id]
    
    def subscribe_to_topics(self, user_id: str, topics: List[str]):
        """Subscribe a user to specified topics"""
        if user_id not in self.topic_subscriptions:
            self.topic_subscriptions[user_id] = set()
        
        self.topic_subscriptions[user_id].update(topics)
        return list(self.topic_subscriptions[user_id])
    
    def unsubscribe_from_topics(self, user_id: str, topics: List[str]):
        """Unsubscribe a user from specified topics"""
        if user_id in self.topic_subscriptions:
            self.topic_subscriptions[user_id].difference_update(topics)
        return list(self.topic_subscriptions[user_id])
                
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
        # # This could be enhanced with a topic subscription mechanism
        # # For now, a simple broadcast as placeholder
        # await self.broadcast({
        message_with_topic = {
            "topic": topic,
            "type": "topic_update",
            "data": message
        }
        json_message = json.dumps(message_with_topic)
        
        # Send to users subscribed to this topic
        for user_id, topics in self.topic_subscriptions.items():
            if topic in topics and user_id in self.active_connections:
                for connection in self.active_connections[user_id]:
                    await connection.send_text(json_message)

# Global connection manager instance
connection_manager = ConnectionManager()
