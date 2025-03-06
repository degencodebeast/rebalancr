from coinbase_agentkit import (
    AgentKit, AgentKitConfig, CdpWalletProvider, CdpWalletProviderConfig,
    cdp_api_action_provider, cdp_wallet_action_provider, 
    erc20_action_provider, pyth_action_provider, weth_action_provider
)
from langchain_openai import ChatOpenAI
from coinbase_agentkit_langchain import get_langchain_tools
from rebalancr.config import Settings
import logging

logger = logging.getLogger(__name__)

class AgentKitService:
    """
    Core service provider for AgentKit functionality.
    Handles initialization, configuration, and provides infrastructure-level operations.
    Implemented as a singleton to ensure consistent access throughout the application.
    """
    _instance = None  # Singleton pattern
    
    @classmethod
    def get_instance(cls, config: Settings = None):
        if cls._instance is None:
            if config is None:
                raise ValueError("Configuration must be provided for AgentKitService initialization.")
            cls._instance = cls(config)
        return cls._instance
    
    def __init__(self, config: Settings):
        """Initialize the AgentKit service with necessary providers and configuration."""
        logger.info("Initializing AgentKitService")
        
        # Initialize wallet provider
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
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.tools = get_langchain_tools(self.agent_kit)
        
        # Store configuration
        self.config = config
        
        logger.info("AgentKitService initialized successfully")
    
    # Core infrastructure methods
    
    async def create_conversation(self, user_id):
        """Create a new conversation in AgentKit."""
        return await self.agent_kit.create_conversation(user_id)
        
    async def send_message(self, conversation_id, content):
        """Send a message to an existing conversation."""
        return await self.agent_kit.send_message(conversation_id, content)
    
    async def execute_smart_contract(self, conversation_id, contract_address, function_name, args):
        """Execute a smart contract call."""
        return await self.agent_kit.smart_contract_write(
            conversation_id=conversation_id,
            contract_address=contract_address,
            function_name=function_name,
            args=args
        )
    
    async def get_user_info(self, conversation_id):
        """Get user information for a conversation."""
        return await self.agent_kit.get_user_info(conversation_id)
        
    def process_custom_intent(self, intent_name, params):
        """
        Process a custom intent based on its name.
        This uses a mapping from intent names to handler functions.
        """
        from rebalancr.intelligence.agent_kit.intent_registry import INTENT_HANDLER_MAP
        if intent_name in INTENT_HANDLER_MAP:
            handler = INTENT_HANDLER_MAP[intent_name]
            return handler(params, self)
        else:
            return f"No handler found for intent '{intent_name}'" 