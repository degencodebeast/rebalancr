import logging
import json
from typing import Dict, Any, Optional

from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage

from ..intelligence.agent_kit.agent_manager import AgentManager
from ..config import Settings, get_settings
from ..websockets.websocket_manager import websocket_manager
from ..api.dependencies import get_agent_manager
from .auth import authenticate_websocket

logger = logging.getLogger(__name__)

async def handle_websocket(websocket: WebSocket):
    """
    Main WebSocket handler with authentication and message routing
    
    This handler:
    1. Authenticates the user with Privy
    2. Routes messages to appropriate handlers based on type
    3. Manages the connection lifecycle
    """
    # Accept the connection
    await websocket.accept()
    
    # Authenticate with Privy
    auth_result = await authenticate_websocket(websocket)
    if not auth_result["success"]:
        logger.error(f"WebSocket authentication failed: {auth_result.get('error')}")
        await websocket.send_json({
            "type": "error",
            "content": "Authentication failed. Please reconnect."
        })
        await websocket.close(code=1008)  # Policy violation
        return
    
    # Get authenticated user ID from Privy
    user_id = auth_result["user_id"]
    logger.info(f"Authenticated user connected: {user_id}")
    
    # Register connection with WebSocket manager
    await websocket_manager.connect(websocket, user_id)
    
    # Get or create wallet for this user
    agent_manager = get_agent_manager()
    try:
        # This will create a wallet if it doesn't exist
        wallet = await agent_manager.wallet_provider.get_or_create_wallet(user_id)
        logger.info(f"Wallet ready for user {user_id}: {wallet.get('address')}")
    except Exception as e:
        logger.error(f"Error initializing wallet for user {user_id}: {str(e)}")
    
    try:
        # Send welcome message
        await websocket_manager.send_personal_message({
            "type": "system",
            "content": "Welcome! I'm your financial assistant. How can I help you today?"
        }, user_id)
        
        # Handle messages with flexibility
        while True:
            # Try to receive as JSON first
            try:
                # Try parsing as JSON
                data = await websocket.receive_json()
                message_type = data.get("type", "chat_message")  # Default to chat_message
                
                # Route to appropriate handler based on message type
                if message_type == "chat_message":
                    message_content = data.get("content", "")  # Use content field from frontend
                    await handle_chat_message(websocket, user_id, {
                        "message": message_content,  # Map to message for internal handlers
                        "conversation_id": data.get("conversation_id", "default")
                    })
                elif message_type == "get_wallet_info":
                    await handle_wallet_info(websocket, user_id, data)
                elif message_type == "get_conversation_history":
                    await handle_get_conversation_history(websocket, user_id, data)
                else:
                    # Unknown message type
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "content": f"Unknown message type: {message_type}"
                    }, user_id)
                
            except json.JSONDecodeError:
                # If not valid JSON, treat as raw text message
                raw_text = await websocket.receive_text()
                
                # Assume it's a chat message
                await handle_chat_message(websocket, user_id, {
                    "message": raw_text,
                    "conversation_id": "default"
                })
                
    except WebSocketDisconnect:
        # Handle disconnect
        logger.info(f"WebSocket disconnected for user {user_id}")
        await websocket_manager.disconnect(websocket, user_id)
    except Exception as e:
        # Handle other errors
        logger.error(f"WebSocket error: {str(e)}")
        await websocket_manager.send_personal_message({
            "type": "error",
            "content": f"Error: {str(e)}"
        }, user_id)
        await websocket_manager.disconnect(websocket, user_id)

async def handle_chat_message(websocket: WebSocket, user_id: str, data: Dict[str, Any]):
    """
    Handle chat messages with streaming response
    
    This handler:
    1. Processes the message with AgentManager
    2. Streams responses in chunks for better UX
    3. Stores conversation history
    """
    try:
        message = data.get("message", "")
        conversation_id = data.get("conversation_id")
        
        if not message:
            await websocket_manager.send_personal_message({
                "type": "error",
                "content": "Message cannot be empty"
            }, user_id)
            return
        
        # Show typing indicator
        await websocket_manager.send_personal_message({
            "type": "typing",
            "content": "Processing your request..."
        }, user_id)
        
        # Get the AgentManager
        agent_manager = get_agent_manager()
        
        # Store user message
        if hasattr(agent_manager, "history_manager"):
            await agent_manager.store_message(
                user_id=user_id,
                message=message,
                message_type="user",
                conversation_id=conversation_id or "default"
            )
        
        # Process with agent via streaming for better UX
        async with agent_manager.get_agent_executor(user_id, conversation_id) as agent_executor:
            # Stream responses from the agent
            async for chunk in agent_executor.astream(
                input={"messages": [HumanMessage(content=message)]},
                config={"configurable": {"thread_id": f"{user_id}-{conversation_id}"}}
            ):
                # Handle agent responses
                if "agent" in chunk:
                    content = chunk["agent"]["messages"][0].content
                    await websocket_manager.send_personal_message({
                        "type": "chat",
                        "content": content,
                        "conversation_id": conversation_id
                    }, user_id)
                
                # Handle tool executions (useful for UI feedback)
                elif "tools" in chunk:
                    tool_content = chunk["tools"]["messages"][0].content
                    await websocket_manager.send_personal_message({
                        "type": "tool",
                        "content": tool_content,
                        "conversation_id": conversation_id
                    }, user_id)
        
        # After streaming is complete, if there was a complete response, store it
        if hasattr(agent_manager, "history_manager") and "content" in locals():
            await agent_manager.store_message(
                user_id=user_id,
                message=content,  # Using the last content chunk
                message_type="agent",
                conversation_id=conversation_id or "default"
            )
            
    except Exception as e:
        logger.error(f"Error handling chat message: {str(e)}")
        await websocket_manager.send_personal_message({
            "type": "error",
            "content": f"Error processing your message: {str(e)}",
            "conversation_id": data.get("conversation_id")
        }, user_id)

async def handle_wallet_info(websocket: WebSocket, user_id: str, data: Dict[str, Any]):
    """
    Handle requests for wallet information
    
    This handler:
    1. Retrieves wallet data for the authenticated user
    2. Returns address and balance information
    """
    try:
        # Get the AgentManager to access wallet provider
        agent_manager = get_agent_manager()
        
        # Get or create wallet for this user
        wallet = await agent_manager.wallet_provider.get_or_create_wallet(user_id)
        
        # Extract address from wallet
        wallet_address = wallet.get("address")
        if not wallet_address:
            wallet_address = agent_manager.wallet_provider.get_address()
        
        # Get wallet balance
        balance = agent_manager.wallet_provider.get_balance(user_id)
        
        # Format balance as human-readable with token symbol
        # Note: Adjust based on your actual implementation
        balance_eth = float(balance) / 10**18  # Convert wei to ETH
        network = agent_manager.wallet_provider.get_network()
        token_symbol = "ETH"  # Default
        
        # Determine token symbol based on network
        if network and network.network_id:
            if "polygon" in network.network_id.lower():
                token_symbol = "MATIC"
            elif "base" in network.network_id.lower():
                token_symbol = "ETH"
            # Add more networks as needed
        
        # Send wallet info back to client
        await websocket_manager.send_personal_message({
            "type": "wallet_info",
            "address": wallet_address,
            "balance": {
                "value": balance_eth,
                "token": token_symbol,
                "raw": str(balance)
            },
            "network": network.network_id if network else "unknown",
            "request_id": data.get("request_id")  # Echo back request ID if provided
        }, user_id)
        
    except Exception as e:
        logger.error(f"Error getting wallet info: {str(e)}")
        await websocket_manager.send_personal_message({
            "type": "error",
            "content": f"Error retrieving wallet information: {str(e)}",
            "request_id": data.get("request_id")
        }, user_id)

async def handle_get_conversation_history(websocket: WebSocket, user_id: str, data: Dict[str, Any]):
    """
    Handle requests for conversation history
    
    This handler retrieves and returns chat history for a specific conversation
    """
    try:
        conversation_id = data.get("conversation_id")
        limit = data.get("limit", 50)
        
        if not conversation_id:
            await websocket_manager.send_personal_message({
                "type": "error",
                "content": "Conversation ID is required"
            }, user_id)
            return
        
        # Get the AgentManager to access history manager
        agent_manager = get_agent_manager()
        
        if not hasattr(agent_manager, "history_manager"):
            await websocket_manager.send_personal_message({
                "type": "error",
                "content": "History manager not available"
            }, user_id)
            return
            
        # Get conversation history
        messages = await agent_manager.history_manager.get_messages(conversation_id, limit)
        
        # Send response
        await websocket_manager.send_personal_message({
            "type": "conversation_history",
            "conversation_id": conversation_id,
            "messages": messages
        }, user_id)
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        await websocket_manager.send_personal_message({
            "type": "error",
            "content": f"Error retrieving conversation history: {str(e)}",
            "request_id": data.get("request_id")
        }, user_id)


# import logging
# from typing import Dict, Any, Optional
# import json

# from fastapi import WebSocket, WebSocketDisconnect
# from langchain_core.messages import HumanMessage

# from ..intelligence.agent_kit.agent_manager import AgentManager
# from ..config import Settings
# from ..websockets.websocket_manager import websocket_manager
# from .auth import authenticate_websocket

# logger = logging.getLogger(__name__)

# # class WebSocketMessageHandler:
# #     """
# #     Handles WebSocket-specific message formatting and sending.
# #     Focuses solely on WebSocket protocol concerns, not agent management.
# #     """
    
# #     def __init__(self, websocket: WebSocket):
# #         """Initialize with a WebSocket connection"""
# #         self.websocket = websocket
    
# #     async def send_message(self, message_type: str, content: Dict[str, Any]):
# #         """Send a formatted message through the WebSocket"""
# #         await self.websocket.send_json({
# #             "type": message_type,
# #             **content
# #         })
    
# #     async def send_welcome(self):
# #         """Send a welcome message to the client"""
# #         await self.send_message("system", {
# #             "content": "Welcome! I'm your financial assistant. How can I help you today?"
# #         })
    
# #     async def send_typing(self):
# #         """Indicate that the agent is processing the message"""
# #         await self.send_message("typing", {
# #             "content": "Processing your request..."
# #         })
    
# #     async def send_error(self, error_message: str):
# #         """Send an error message to the client"""
# #         await self.send_message("error", {
# #             "content": error_message
# #         })

# async def handle_chat_websocket(websocket: WebSocket, user_id: str, session_id: Optional[str] = None):
#     """
#     WebSocket handler for chat interactions using the AgentManager
    
#     This function focuses solely on WebSocket protocol concerns, while delegating
#     agent management to the AgentManager class.
    
#     Args:
#         websocket: WebSocket connection
#         user_id: User identifier
#         session_id: Optional session identifier
#     """
#     try:
#         # Accept the connection here
#         await websocket.accept()
        
#         # Then register with manager
#         await websocket_manager.connect(websocket, user_id)
        
#         settings = Settings()
#         agent_manager = AgentManager.get_instance(settings)
        
#         # Send welcome message
#         await websocket_manager.send_personal_message({
#             "type": "system",
#             "content": "Welcome! I'm your financial assistant. How can I help you today?"
#         }, user_id)
        
#         while True:
#             # # Use receive_json if expecting JSON data
#             # data = await websocket.receive_json()

#             #Use receive_text if expecting text data
#             data = await websocket.receive_text()
#             message = data.get("message", "")
            
#             if not message:
#                 await websocket_manager.send_personal_message({
#                     "type": "error",
#                     "message": "Empty message received"
#                 }, user_id)
#                 continue
                
#             # Show typing indicator
#             await websocket_manager.send_personal_message({
#                 "type": "typing",
#                 "content": "Processing your request..."
#             }, user_id)
            
#             # Process with agent via AgentManager
#             async with agent_manager.get_agent_executor(user_id, session_id) as agent_executor:
#                 # Stream responses from the agent
#                 async for chunk in agent_executor.astream(
#                     input={"messages": [HumanMessage(content=message)]},
#                     config={"configurable": {"thread_id": f"{user_id}-{session_id}"}}
#                 ):
#                     # Handle agent responses
#                     if "agent" in chunk:
#                         content = chunk["agent"]["messages"][0].content
#                         await websocket_manager.send_personal_message({
#                             "type": "chat",
#                             "content": content
#                         }, user_id)
                    
#                     # Handle tool executions
#                     elif "tools" in chunk:
#                         content = chunk["tools"]["messages"][0].content
#                         await websocket_manager.send_personal_message({
#                             "type": "tool",
#                             "content": content
#                         }, user_id)
                        
#     except WebSocketDisconnect:
#         logger.info(f"WebSocket disconnected for user {user_id}")
#         await websocket_manager.disconnect(websocket, user_id)
#     except json.JSONDecodeError:
#         logger.error("Received invalid JSON data")
#         await websocket_manager.disconnect(websocket, user_id)
#     except Exception as e:
#         logger.error(f"WebSocket error: {str(e)}")
#         await websocket_manager.disconnect(websocket, user_id)





























# #NOTE: This is not used anymore, but I'm keeping it here for reference
# # new chat handler is in websockets/chat_handler.py

# # import logging
# # import json
# # from typing import Dict, Any, Optional
# # import asyncio
# # from fastapi import WebSocket

# # from ..intelligence.agent_kit.chat_agent import PortfolioAgent
# # from ..chat.history_manager import ChatHistoryManager
# # from .websocket import connection_manager

# # logger = logging.getLogger(__name__)

# # class ChatWebSocketHandler:
# #     """
# #     Handler for WebSocket chat connections
    
# #     Processes messages from clients and manages responses
# #     """
    
# #     def __init__(self, portfolio_agent: PortfolioAgent, chat_history_manager: ChatHistoryManager):
# #         """
# #         Initialize the WebSocket handler
        
# #         Args:
# #             portfolio_agent: PortfolioAgent instance for handling portfolio-related queries
# #             chat_history_manager: ChatHistoryManager for storing and retrieving chat history
# #         """
# #         self.portfolio_agent = portfolio_agent
# #         self.chat_history_manager = chat_history_manager
        
# #     async def handle_message(self, websocket: WebSocket, user_id: str, data: Dict[str, Any]):
# #         """
# #         Handle a message from a client
        
# #         Args:
# #             websocket: WebSocket connection
# #             user_id: User identifier
# #             data: Message data
# #         """
# #         try:
# #             message_type = data.get("type", "")
            
# #             if message_type == "chat_message":
# #                 await self.handle_chat_message(user_id, data)
# #             elif message_type == "get_conversation_history":
# #                 await self.handle_get_conversation_history(user_id, data)
# #             elif message_type == "get_conversations":
# #                 await self.handle_get_conversations(user_id, data)
# #             else:
# #                 # Unknown message type
# #                 await connection_manager.send_personal_message(
# #                     {
# #                         "type": "error",
# #                         "message": f"Unknown message type: {message_type}"
# #                     },
# #                     user_id
# #                 )
# #         except Exception as e:
# #             logger.error(f"Error handling message: {str(e)}")
# #             await connection_manager.send_personal_message(
# #                 {
# #                     "type": "error",
# #                     "message": f"Error processing message: {str(e)}"
# #                 },
# #                 user_id
# #             )
            
# #     async def handle_chat_message(self, user_id: str, data: Dict[str, Any]):
# #         """
# #         Handle a chat message from a client
        
# #         Args:
# #             user_id: User identifier
# #             data: Message data
# #         """
# #         message = data.get("message", "")
# #         conversation_id = data.get("conversation_id")
        
# #         if not message:
# #             await connection_manager.send_personal_message(
# #                 {
# #                     "type": "error",
# #                     "message": "Message cannot be empty"
# #                 },
# #                 user_id
# #             )
# #             return
            
# #         # Store user message
# #         await self.chat_history_manager.add_message({
# #             "user_id": user_id,
# #             "conversation_id": conversation_id,
# #             "message": message,
# #             "message_type": "user",
# #         })
        
# #         # Process message with portfolio agent
# #         try:
# #             async for chunk in self.portfolio_agent.chat(
# #                 user_id=user_id,
# #                 message=message,
# #                 conversation_id=conversation_id
# #             ):
# #                 # Send each chunk as it becomes available
# #                 await connection_manager.send_personal_message(
# #                     {
# #                         "type": "chat_response",
# #                         "message": chunk,
# #                         "conversation_id": conversation_id
# #                     },
# #                     user_id
# #                 )
# #         except Exception as e:
# #             logger.error(f"Error processing chat message: {str(e)}")
# #             await connection_manager.send_personal_message(
# #                 {
# #                     "type": "error",
# #                     "message": f"Error processing message: {str(e)}"
# #                 },
# #                 user_id
# #             )
            
# #     async def handle_get_conversation_history(self, user_id: str, data: Dict[str, Any]):
# #         """
# #         Handle a request for conversation history
        
# #         Args:
# #             user_id: User identifier
# #             data: Request data
# #         """
# #         conversation_id = data.get("conversation_id")
# #         limit = data.get("limit", 50)
        
# #         if not conversation_id:
# #             await connection_manager.send_personal_message(
# #                 {
# #                     "type": "error",
# #                     "message": "Conversation ID is required"
# #                 },
# #                 user_id
# #             )
# #             return
            
# #         # Get conversation history
# #         messages = await self.chat_history_manager.get_messages(conversation_id, limit)
        
# #         # Send response
# #         await connection_manager.send_personal_message(
# #             {
# #                 "type": "conversation_history",
# #                 "conversation_id": conversation_id,
# #                 "messages": messages
# #             },
# #             user_id
# #         )
        
# #     async def handle_get_conversations(self, user_id: str, data: Dict[str, Any]):
# #         """
# #         Handle a request for user conversations
        
# #         Args:
# #             user_id: User identifier
# #             data: Request data
# #         """
# #         limit = data.get("limit", 10)
        
# #         # Get user conversations
# #         conversations = await self.chat_history_manager.get_user_conversations(user_id, limit)
        
# #         # Send response
# #         await connection_manager.send_personal_message(
# #             {
# #                 "type": "conversations",
# #                 "conversations": conversations
# #             },
# #             user_id
# #         ) 