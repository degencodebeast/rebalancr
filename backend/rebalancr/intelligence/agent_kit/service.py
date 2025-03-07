from coinbase_agentkit import (
    AgentKit, AgentKitConfig, CdpWalletProvider, CdpWalletProviderConfig,
    cdp_api_action_provider, cdp_wallet_action_provider, 
    erc20_action_provider, pyth_action_provider, weth_action_provider
)
from langchain_openai import ChatOpenAI
from coinbase_agentkit_langchain import get_langchain_tools
from ...config import Settings
import logging
from ...intelligence.agent_kit.intent_registry import INTENT_HANDLER_MAP

logger = logging.getLogger(__name__)

class AgentKitService:
    """
    Core infrastructure service for AgentKit functionality.
    
    This service focuses exclusively on low-level infrastructure concerns:
    - Initializing SDK components
    - Providing action providers
    - Managing LLM instances
    - Exposing core AgentKit operations
    
    It does NOT handle:
    - User-specific wallet data (handled by AgentManager)
    - WebSocket communication (handled by WebSocketMessageHandler)
    - Business logic (handled by AgentKitClient)
    """
    _instance = None  # Singleton pattern
    
    @classmethod
    def get_instance(cls, config: Settings):
        """Get singleton instance of AgentKitService"""
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance
        
    
    def __init__(self, config: Settings):
        """Initialize the AgentKit service with SDK configuration."""
        logger.info("Initializing AgentKitService")
        
        # Initialize with a default wallet provider
        # Note: User-specific wallet data is handled by AgentManager
        wallet_provider_config = CdpWalletProviderConfig(
            api_key_name=config.CDP_API_KEY_NAME,
            api_key_private_key=config.CDP_API_KEY_PRIVATE_KEY
        )
        self.wallet_provider = CdpWalletProvider(wallet_provider_config)
        
        # Initialize AgentKit with action providers
        self.agent_kit = AgentKit(AgentKitConfig(
            wallet_provider=self.wallet_provider,
            action_providers=[
                cdp_api_action_provider(),
                cdp_wallet_action_provider(),
                erc20_action_provider(),
                pyth_action_provider(),
                weth_action_provider()
            ]
        ))
        
        # For LangChain integration
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL or "gpt-4o-mini",
            api_key=config.OPENAI_API_KEY
        )
        self.tools = get_langchain_tools(self.agent_kit)
        
        # Store configuration
        self.config = config
        
        logger.info("AgentKitService initialized successfully")
    
    # Infrastructure-level methods only
    
    async def create_conversation(self, user_id):
        """Create a new conversation in AgentKit."""
        return await self.agent_kit.create_conversation(user_id)
        
    async def send_message(self, conversation_id, content):
        """Send a message to an existing conversation."""
        return await self.agent_kit.send_message(conversation_id, content)
    
    async def execute_smart_contract(self, contract_address, function_name, args, **kwargs):
        """Execute a smart contract call."""
        return await self.agent_kit.smart_contract_write(
            contract_address=contract_address,
            function_name=function_name,
            args=args,
            **kwargs
        )
    
    async def get_wallet_info(self, wallet_address):
        """Get information about a wallet."""
        return await self.agent_kit.get_wallet_info(wallet_address)
    
    def get_action_providers(self):
        """Get the registered action providers."""
        return self.agent_kit.action_providers
    
    def process_custom_intent(self, intent_name, params):
        """
        Process a custom intent based on its name.
        This uses a mapping from intent names to handler functions.
        """
        if intent_name in INTENT_HANDLER_MAP:
            handler = INTENT_HANDLER_MAP[intent_name]
            return handler(params, self)
        else:
            return f"No handler found for intent '{intent_name}'" 