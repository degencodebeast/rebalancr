from ..intelligence.agent_kit.chat_agent import PortfolioAgent
from ..chat.history_manager import ChatHistoryManager
import asyncio
import uuid
from datetime import datetime

class ChatService:
    def __init__(self, portfolio_agent, chat_history_manager):
        """
        Initialize the chat service
        
        Args:
            portfolio_agent: PortfolioAgent instance for handling portfolio-related queries
            chat_history_manager: ChatHistoryManager for storing and retrieving chat history
        """
        self.portfolio_agent = portfolio_agent
        self.chat_history_manager = chat_history_manager
        
    async def process_message(self, user_id, message, conversation_id=None):
        """
        Process a user message and generate a response
        
        Args:
            user_id: User identifier
            message: User message content
            conversation_id: Optional conversation ID
            
        Returns:
            An async generator that yields response chunks
        """
        # Generate conversation_id if not provided
        if not conversation_id:
            conversation_id = f"conv_{uuid.uuid4()}"
            
        # Store user message
        await self.chat_history_manager.add_message({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message": message,
            "message_type": "user",
            "timestamp": datetime.now().isoformat()
        })
        
        # Process message with portfolio agent
        response_generator = self.portfolio_agent.chat(
            user_id=user_id,
            message=message,
            conversation_id=conversation_id
        )
        
        # Stream response chunks
        async for chunk in response_generator:
            # Store agent response chunk
            response_data = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message": chunk,
                "message_type": "agent",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.chat_history_manager.add_message(response_data)
            
            # Yield response chunk for streaming
            yield {
                "type": "chat_response",
                "content": chunk,
                "conversation_id": conversation_id
            }
            
            # Small delay to simulate streaming
            await asyncio.sleep(0.05)
            
    async def get_conversation_history(self, user_id, conversation_id, limit=50):
        """
        Get conversation history
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        return await self.chat_history_manager.get_messages(conversation_id, limit)
        
    async def get_user_conversations(self, user_id, limit=10):
        """
        Get list of conversations for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation dictionaries
        """
        return await self.chat_history_manager.get_user_conversations(user_id, limit)
