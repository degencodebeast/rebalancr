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
)
from coinbase_agentkit_langchain import get_langchain_tools
from ...database import db_manager

from ...config import Settings
from .service import AgentKitService
from ...chat.history_manager import ChatHistoryManager

logger = logging.getLogger(__name__)

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
    def get_instance(cls, settings: Settings = None):
        """Get singleton instance of AgentManager"""
        if cls._instance is None:
            if settings is None:
                raise ValueError("Settings must be provided for AgentManager initialization")
            cls._instance = cls(settings)
        return cls._instance
    
    def __init__(self, settings: Settings):
        """Initialize the AgentManager with settings"""
        self.settings = settings
        self.service = AgentKitService.get_instance(settings)
        self.sqlite_path = settings.sqlite_db_path or "sqlite:///conversations.db"
        self.wallet_data_dir = settings.wallet_data_dir or "./data/wallets"
        
        # Ensure wallet data directory exists
        os.makedirs(self.wallet_data_dir, exist_ok=True)
        
        logger.info("AgentManager initialized with wallet directory: %s", self.wallet_data_dir)
        
        self.history_manager = ChatHistoryManager(db_manager)
    
    def _get_wallet_path(self, user_id: str) -> str:
        """Get wallet data file path for a user"""
        return os.path.join(self.wallet_data_dir, f"wallet-{user_id}.json")
    
    async def load_wallet_data(self, user_id: str) -> Optional[str]:
        """Load wallet data for a user if it exists"""
        wallet_data_path = self._get_wallet_path(user_id)
        
        if os.path.exists(wallet_data_path):
            try:
                with open(wallet_data_path, "r") as f:
                    wallet_data = f.read()
                    logger.info("Loaded wallet data for user %s", user_id)
                    return wallet_data
            except Exception as e:
                logger.error("Error reading wallet data for user %s: %s", user_id, str(e))
        
        logger.info("No existing wallet data found for user %s", user_id)
        return None
    
    async def save_wallet_data(self, user_id: str, wallet_provider: CdpWalletProvider) -> None:
        """Save wallet data for a user"""
        wallet_data_path = self._get_wallet_path(user_id)
        
        try:
            # Export and save wallet data
            wallet_data = json.dumps(wallet_provider.export_wallet().to_dict())
            with open(wallet_data_path, "w") as f:
                f.write(wallet_data)
            logger.info("Saved wallet data for user %s", user_id)
        except Exception as e:
            logger.error("Error saving wallet data for user %s: %s", user_id, str(e))
    
    async def initialize_agentkit(self, user_id: str) -> AgentKit:
        """Initialize AgentKit with user-specific wallet data"""
        # Load existing wallet data if available
        wallet_data = await self.load_wallet_data(user_id)
        
        # Configure wallet provider
        cdp_config = None
        if wallet_data:
            cdp_config = CdpWalletProviderConfig(wallet_data=wallet_data)
        
        # Initialize wallet provider
        wallet_provider = CdpWalletProvider(cdp_config)
        
        # Initialize AgentKit with action providers from service
        agentkit = AgentKit(
            AgentKitConfig(
                wallet_provider=wallet_provider,
                action_providers=self.service.agent_kit.config.action_providers,
            )
        )
        
        # Save updated wallet data
        await self.save_wallet_data(user_id, wallet_provider)
        
        return agentkit
    
    @contextlib.asynccontextmanager
    async def get_agent_executor(self, user_id: str, session_id: Optional[str] = None) -> AsyncIterator:
        """
        Get a ReAct agent executor with SQLite persistence and wallet data
        
        Args:
            user_id: User identifier
            session_id: Optional session identifier
            
        Returns:
            AsyncIterator to a configured agent executor
        """
        # Create a unique thread ID for this user/session
        thread_id = f"{user_id}-{session_id}" if session_id else f"{user_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Initialize AgentKit with user's wallet data
        agentkit = await self.initialize_agentkit(user_id)
        
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
            user_id: User identifier
            message: User message
            session_id: Optional session identifier
            
        Returns:
            Agent response as string
        """
        thread_id = f"{user_id}-{session_id}" if session_id else user_id
        config = {"configurable": {"thread_id": thread_id}}
        
        response = ""
        async with self.get_agent_executor(user_id) as agent_executor:
            async for chunk in agent_executor.astream(
                input={"messages": [HumanMessage(content=message)]},
                config=config
            ):
                if "agent" in chunk:
                    response += chunk["agent"]["messages"][0].content
        
        return response
    
    async def get_chat_history(self, user_id: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get chat history for a user and optional session
        
        Args:
            user_id: User identifier
            session_id: Optional session identifier
            
        Returns:
            List of message dictionaries with content and isUser flag
        """
        thread_id = f"{user_id}-{session_id}" if session_id else user_id
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