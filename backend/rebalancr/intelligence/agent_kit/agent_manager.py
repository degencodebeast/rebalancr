import contextlib
import json
import os
import logging
from typing import AsyncIterator, Dict, List, Any, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    CdpWalletProviderConfig,
    WalletProvider
)
from coinbase_agentkit_langchain import get_langchain_tools
from rebalancr.config import Settings

# REMOVE these imports to break circular dependency
# from ...api.dependencies import get_chat_history_manager, get_db_manager

from ...chat.history_manager import ChatHistoryManager
from ...database.db_manager import DatabaseManager
from .wallet_provider import PrivyWalletProvider

logger = logging.getLogger(__name__)


# Client Layer (business logic)
#     ↓ calls
# Service Layer (send_message)
#     ↓ calls 
# Agent Manager (get_agent_response)
#     ↓ uses
# ReAct Pattern Implementation

class AgentManager:
    """
    Manages LLM agents with persistent conversations and wallet data
    
    This is responsible for:
    1. Initializing AgentKit with proper configuration
    2. Managing wallet data persistence
    3. Creating and running ReAct agents
    4. Handling chat history and conversation persistence
    """
    
    _instance = None  # Singleton pattern
    
    @classmethod
    def get_instance(cls, config: Settings):
        """Get singleton instance of AgentManager"""
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance
    
    def __init__(self, settings: Settings):
        """Initialize the AgentManager with settings"""
        self.settings = settings
        self.sqlite_path = settings.sqlite_db_path or "sqlite:///conversations.db"
        self.wallet_data_dir = settings.wallet_data_dir or "./data/wallets"
        
        # Initialize direct instances instead of using getters
        self.db_manager = DatabaseManager()  # Direct init instead of get_db_manager()
        self.history_manager = ChatHistoryManager(db_manager=self.db_manager)  # Direct init
        
        # Initialize PrivyWalletProvider instead of CDP wallet provider
        self.wallet_provider = PrivyWalletProvider.get_instance(settings)

        from .service import AgentKitService
        self.service = AgentKitService.get_instance(settings)

        # Ensure wallet data directory exists
        os.makedirs(self.wallet_data_dir, exist_ok=True)
        
        logger.info("AgentManager initialized with wallet directory: %s", self.wallet_data_dir)
        
    def _normalize_user_id(self, user_id: str) -> str:
        """Normalize Privy user IDs (handles both did:privy: format and regular format)"""
        if user_id and user_id.startswith("did:privy:"):
            return user_id.replace("did:privy:", "")
        return user_id

    def set_action_providers(self, action_providers):
        """Set action providers for this manager"""
        self.action_providers = action_providers
        logger.info(f"Set {len(action_providers)} action providers for AgentManager")

    async def initialize_agent_for_user(self, user_id: str) -> AgentKit:
        """Initialize wallet and return configured AgentKit"""
        # Normalize user ID
        normalized_user_id = self._normalize_user_id(user_id)
        
        # Get or create wallet for user
        await self.wallet_provider.get_or_create_wallet(normalized_user_id)
        
        # Get shared AgentKit from service - NO NEW INSTANCE
        return self.service.get_agent_kit()
    
    @contextlib.asynccontextmanager
    async def get_agent_executor(self, user_id: str, session_id: Optional[str] = None) -> AsyncIterator:
        """
        Get a ReAct agent executor with SQLite persistence and wallet data
        
        Args:
            user_id: User identifier from Privy authentication
            session_id: Optional session identifier
            
        Returns:
            AsyncIterator to a configured agent executor
        """
        # Create a unique thread ID for this user/session
        normalized_user_id = self._normalize_user_id(user_id)
        thread_id = f"{normalized_user_id}-{session_id}" if session_id else f"{normalized_user_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Initialize AgentKit with user's wallet data
        agentkit = await self.initialize_agent_for_user(normalized_user_id)
        
        # Get tools using helper function
        tools = get_langchain_tools(agentkit)
        
        # Set up SQLite persistence
        async with AsyncSqliteSaver.from_conn_string(self.sqlite_path) as checkpointer:
            yield create_react_agent(
                model=self.service.llm,
                tools=tools,
                checkpointer=checkpointer,
                state_modifier=(
                    "You are a financial assistant that helps users manage their portfolios and find "
                    "the best investment opportunities. You can perform on-chain transactions when requested. "
                    "Always explain what actions you're taking and why. If you encounter a technical error, "
                    "ask the user to try again later. Only use the tools available to you."
                ),
            )
    
    async def get_agent_response(self, user_id: str, message: str, session_id: Optional[str] = None) -> str:
        """
        Get a response from the agent for a given message (non-WebSocket method)
        
        Args:
            user_id: User identifier from Privy authentication
            message: User message
            session_id: Optional session identifier
            
        Returns:
            Agent response as string
        """
        normalized_user_id = self._normalize_user_id(user_id)
        thread_id = f"{normalized_user_id}-{session_id}" if session_id else f"{normalized_user_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Store user message in history
        conversation_id = session_id or "default"
        #check to be sure that this does not clash with store_message function
        #conversation_id = self.db_manager.create_conversation(normalized_user_id)
        await self.store_message(normalized_user_id, message, "user", conversation_id)
        
        response = ""
        async with self.get_agent_executor(normalized_user_id) as agent_executor:
            async for chunk in agent_executor.astream(
                input={"messages": [HumanMessage(content=message)]},
                config=config
            ):
                if "agent" in chunk:
                    response += chunk["agent"]["messages"][0].content
        
        # Store agent response in history
        await self.store_message(normalized_user_id, response, "agent", conversation_id)
        
        return response
    
    async def get_chat_history(self, user_id: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get chat history for a user and optional session
        
        Args:
            user_id: User identifier from Privy authentication
            session_id: Optional session identifier
            
        Returns:
            List of message dictionaries with content and isUser flag
        """
        normalized_user_id = self._normalize_user_id(user_id)
        thread_id = f"{normalized_user_id}-{session_id}" if session_id else f"{normalized_user_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Default welcome messages
        messages = [
            {
                'content': 'Welcome! I\'m your financial assistant.',
                'isUser': False,
            },
            {
                'content': 'I can help you manage your portfolio and find the best investment opportunities.',
                'isUser': False,
            }
        ]
        
        # Get conversation history from LangGraph
        async with AsyncSqliteSaver.from_conn_string(self.sqlite_path) as checkpointer:
            checkpoint = await checkpointer.aget(config=config)
            if checkpoint:
                for message in checkpoint.get('channel_values', {}).get('messages', []):
                    if isinstance(message, (HumanMessage, AIMessage)):
                        messages.append({
                            "content": message.content,
                            "isUser": isinstance(message, HumanMessage),
                        })
        
        return messages
    
    async def store_message(self, user_id, message, message_type, conversation_id):
        # Store in database via history manager
        return await self.history_manager.store_message(
            user_id, message, message_type, conversation_id
        ) 