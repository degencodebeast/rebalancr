from coinbase_agentkit import (
    AgentKit, AgentKitConfig, CdpWalletProvider, CdpWalletProviderConfig,
    cdp_api_action_provider, cdp_wallet_action_provider, 
    # other action providers
)
from langchain_openai import ChatOpenAI
from coinbase_agentkit_langchain import get_langchain_tools
from rebalancr.config import Settings

class AgentKitService:
    _instance = None  # Singleton pattern
    
    @classmethod
    def get_instance(cls, config: Settings = None):
        if cls._instance is None:
            if config is None:
                raise ValueError("Configuration must be provided for AgentKitService initialization.")
            cls._instance = cls(config)
        return cls._instance
    
    def __init__(self, config: Settings):
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
                # Add other needed providers
            ]
        ))
        
        # For LangChain integration
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.tools = get_langchain_tools(self.agent_kit)
    
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