#NOTE: This is not used anymore, but I'm keeping it here for reference
# new chat handler is in websockets/chat_handler.py

# import logging
# import json
# from typing import Dict, Any, Optional
# import asyncio
# from fastapi import WebSocket

# from ..intelligence.agent_kit.chat_agent import PortfolioAgent
# from ..chat.history_manager import ChatHistoryManager
# from .websocket import connection_manager

# logger = logging.getLogger(__name__)

# class ChatWebSocketHandler:
#     """
#     Handler for WebSocket chat connections
    
#     Processes messages from clients and manages responses
#     """
    
#     def __init__(self, portfolio_agent: PortfolioAgent, chat_history_manager: ChatHistoryManager):
#         """
#         Initialize the WebSocket handler
        
#         Args:
#             portfolio_agent: PortfolioAgent instance for handling portfolio-related queries
#             chat_history_manager: ChatHistoryManager for storing and retrieving chat history
#         """
#         self.portfolio_agent = portfolio_agent
#         self.chat_history_manager = chat_history_manager
        
#     async def handle_message(self, websocket: WebSocket, user_id: str, data: Dict[str, Any]):
#         """
#         Handle a message from a client
        
#         Args:
#             websocket: WebSocket connection
#             user_id: User identifier
#             data: Message data
#         """
#         try:
#             message_type = data.get("type", "")
            
#             if message_type == "chat_message":
#                 await self.handle_chat_message(user_id, data)
#             elif message_type == "get_conversation_history":
#                 await self.handle_get_conversation_history(user_id, data)
#             elif message_type == "get_conversations":
#                 await self.handle_get_conversations(user_id, data)
#             else:
#                 # Unknown message type
#                 await connection_manager.send_personal_message(
#                     {
#                         "type": "error",
#                         "message": f"Unknown message type: {message_type}"
#                     },
#                     user_id
#                 )
#         except Exception as e:
#             logger.error(f"Error handling message: {str(e)}")
#             await connection_manager.send_personal_message(
#                 {
#                     "type": "error",
#                     "message": f"Error processing message: {str(e)}"
#                 },
#                 user_id
#             )
            
#     async def handle_chat_message(self, user_id: str, data: Dict[str, Any]):
#         """
#         Handle a chat message from a client
        
#         Args:
#             user_id: User identifier
#             data: Message data
#         """
#         message = data.get("message", "")
#         conversation_id = data.get("conversation_id")
        
#         if not message:
#             await connection_manager.send_personal_message(
#                 {
#                     "type": "error",
#                     "message": "Message cannot be empty"
#                 },
#                 user_id
#             )
#             return
            
#         # Store user message
#         await self.chat_history_manager.add_message({
#             "user_id": user_id,
#             "conversation_id": conversation_id,
#             "message": message,
#             "message_type": "user",
#         })
        
#         # Process message with portfolio agent
#         try:
#             async for chunk in self.portfolio_agent.chat(
#                 user_id=user_id,
#                 message=message,
#                 conversation_id=conversation_id
#             ):
#                 # Send each chunk as it becomes available
#                 await connection_manager.send_personal_message(
#                     {
#                         "type": "chat_response",
#                         "message": chunk,
#                         "conversation_id": conversation_id
#                     },
#                     user_id
#                 )
#         except Exception as e:
#             logger.error(f"Error processing chat message: {str(e)}")
#             await connection_manager.send_personal_message(
#                 {
#                     "type": "error",
#                     "message": f"Error processing message: {str(e)}"
#                 },
#                 user_id
#             )
            
#     async def handle_get_conversation_history(self, user_id: str, data: Dict[str, Any]):
#         """
#         Handle a request for conversation history
        
#         Args:
#             user_id: User identifier
#             data: Request data
#         """
#         conversation_id = data.get("conversation_id")
#         limit = data.get("limit", 50)
        
#         if not conversation_id:
#             await connection_manager.send_personal_message(
#                 {
#                     "type": "error",
#                     "message": "Conversation ID is required"
#                 },
#                 user_id
#             )
#             return
            
#         # Get conversation history
#         messages = await self.chat_history_manager.get_messages(conversation_id, limit)
        
#         # Send response
#         await connection_manager.send_personal_message(
#             {
#                 "type": "conversation_history",
#                 "conversation_id": conversation_id,
#                 "messages": messages
#             },
#             user_id
#         )
        
#     async def handle_get_conversations(self, user_id: str, data: Dict[str, Any]):
#         """
#         Handle a request for user conversations
        
#         Args:
#             user_id: User identifier
#             data: Request data
#         """
#         limit = data.get("limit", 10)
        
#         # Get user conversations
#         conversations = await self.chat_history_manager.get_user_conversations(user_id, limit)
        
#         # Send response
#         await connection_manager.send_personal_message(
#             {
#                 "type": "conversations",
#                 "conversations": conversations
#             },
#             user_id
#         ) 