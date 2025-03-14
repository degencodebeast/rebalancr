from coinbase_agentkit import (
    AgentKit, AgentKitConfig, CdpWalletProvider, CdpWalletProviderConfig,
    cdp_api_action_provider, cdp_wallet_action_provider, 
    erc20_action_provider, morpho_action_provider, pyth_action_provider, wallet_action_provider, weth_action_provider, wow_action_provider
)
#from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek

from coinbase_agentkit_langchain import get_langchain_tools
from langchain_openai import ChatOpenAI
from rebalancr.execution.providers.kuru import kuru_action_provider
from rebalancr.execution.providers.market_action import market_action_provider
from ...config import Settings
import logging

logger = logging.getLogger(__name__)

# Client Layer (business logic)
#     ↓ calls
# Service Layer (send_message)
#     ↓ calls 
# Agent Manager (get_agent_response)
#     ↓ uses
# ReAct Pattern Implementation

class AgentKitService:
    """
    Core service provider for AgentKit functionality.
    Handles initialization, configuration, and provides infrastructure-level operations.
    Implemented as a singleton to ensure consistent access throughout the application.
    """
    _instance = None  # Singleton pattern
    
    @classmethod
    def get_instance(cls, config: Settings, wallet_provider=None, agent_manager=None):
        """Get singleton instance of AgentKitService"""
        if cls._instance is None:
            cls._instance = cls(config, wallet_provider, agent_manager)
        elif wallet_provider is not None:
            cls._instance.set_wallet_provider(wallet_provider)
        elif agent_manager is not None:
            cls._instance.set_agent_manager(agent_manager)
        return cls._instance
    
    def __init__(self, config: Settings, wallet_provider=None, agent_manager=None):
        """Initialize the AgentKit service with necessary providers and configuration."""
        logger.info("Initializing AgentKitService")
        
        # Store dependencies passed in rather than importing getters
        self.wallet_provider = wallet_provider  # Will be set later if None
        self.agent_manager = agent_manager      # Will be set later if None
        
        # Initialize AgentKit with basic action providers
        self.agent_kit = AgentKit(AgentKitConfig(
            wallet_provider=self.wallet_provider if self.wallet_provider else None,
            #action_providers=self._get_base_action_providers()
            action_providers=[
                
                #cdp_wallet_action_provider(),
                erc20_action_provider(),
                pyth_action_provider(),
                weth_action_provider(),
                kuru_action_provider(),
                wallet_action_provider(),
                # market_action_provider(
                #     allora_client=None,
                #     market_analyzer=None,
                #     market_data_service=None
                # ),
                #wallet_action_provider(),
                morpho_action_provider(),
                wow_action_provider(),
                ##allora_action_provider(),
            ]
        ))

        # self.llm = ChatDeepSeek(
        #     model=config.DEEPSEEK_MODEL,
        #     api_key=config.DEEPSEEK_API_KEY,
        #     temperature=0,
        #     max_tokens=None,
        #     timeout=None,
        # )
        
        # For LangChain integration
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL or "gpt-4o-mini",
            api_key=config.OPENAI_API_KEY
        )
        self.tools = get_langchain_tools(self.agent_kit)
        
        # Store configuration
        self.config = config
        
        logger.info("AgentKitService initialized successfully")
    
    def set_wallet_provider(self, wallet_provider):
        """Set wallet provider after initialization"""
        self.wallet_provider = wallet_provider
        if self.agent_kit:
            self.agent_kit.wallet_provider = wallet_provider
            
    def set_agent_manager(self, agent_manager):
        """Set agent manager after initialization"""
        self.agent_manager = agent_manager
    
    def get_agent_kit(self):
        """Get the shared AgentKit instance"""
        return self.agent_kit

    def _get_base_action_providers(self):
        """Get the base action providers without circular dependencies"""
        return [
            cdp_api_action_provider(
                CdpWalletProviderConfig(

                )
            ),
            cdp_wallet_action_provider(),
            erc20_action_provider(),
            pyth_action_provider(),
            weth_action_provider(),
            kuru_action_provider(),
            market_action_provider(
                allora_client=None,
                market_analyzer=None,
                market_data_service=None
            ),
            #wallet_action_provider(),
            morpho_action_provider(),
            wow_action_provider(),
        ]
        
    def register_portfolio_provider(self, portfolio_provider):
        """Register the portfolio provider after IntelligenceEngine is initialized"""
        self.agent_kit.action_providers.append(portfolio_provider)
        # Update tools for LangChain
        self.tools = get_langchain_tools(self.agent_kit)
        logger.info("Portfolio provider registered successfully")

    def register_rebalancer_provider(self, rebalancer_provider):
        """Register the rebalancer provider after IntelligenceEngine is initialized"""
        self.agent_kit.action_providers.append(rebalancer_provider)
        # Update tools for LangChain
        self.tools = get_langchain_tools(self.agent_kit)
        logger.info("Rebalancer provider registered successfully")
        
    def get_action_providers(self):
        """Get the registered action providers."""
        return self.agent_kit.action_providers
        
    async def send_message(self, conversation_id, content):
        """Send a message to an existing conversation."""
        if self.agent_manager:
            return await self.agent_manager.get_agent_response(conversation_id, content)
        else:
            logger.error("Agent manager not set, cannot send message")
            raise RuntimeError("Agent manager not initialized")

