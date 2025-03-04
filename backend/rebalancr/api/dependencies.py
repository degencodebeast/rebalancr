from fastapi import Depends
from rebalancr.intelligence.agent_kit.wallet_provider import get_wallet_provider

from ..database.db_manager import DatabaseManager
from ..intelligence.agent_kit.chat_agent import PortfolioAgent
from ..intelligence.agent_kit.trade_agent import TradeAgent
from ..intelligence.allora.client import AlloraClient
from ..strategy.engine import StrategyEngine
from .websockets.websocket_manager import WebSocketManager
from .services.chat_service import ChatService
from ..execution.action_registry import ActionRegistry
from ..execution.actions.trade_actions import TradeAction, RebalanceAction
from ..execution.actions.portfolio_actions import AnalyzePortfolioAction
from ..agent.agent_kit import RebalancerAgentKit
from ..config import get_settings
from ..intelligence.agent_kit.wallet_provider import WalletProvider
from ..execution.action_provider import TradeActionProvider

# Singletons
_db_manager = None
_allora_client = None
_strategy_engine = None
_trade_agent = None
_portfolio_agent = None
_websocket_manager = None
_chat_service = None
_action_registry = None

def get_db_manager():
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def get_allora_client():
    global _allora_client
    if _allora_client is None:
        _allora_client = AlloraClient()
    return _allora_client

def get_strategy_engine():
    global _strategy_engine
    if _strategy_engine is None:
        _strategy_engine = StrategyEngine()
    return _strategy_engine

def get_trade_agent():
    global _trade_agent
    if _trade_agent is None:
        db_manager = get_db_manager()
        _trade_agent = TradeAgent(db_manager, None)  # Replace None with market_analyzer when available
    return _trade_agent

def get_action_registry():
    global _action_registry
    if _action_registry is None:
        _action_registry = ActionRegistry()
        
        # Get dependencies
        db_manager = get_db_manager()
        trade_agent = get_trade_agent()
        strategy_engine = get_strategy_engine()
        
        # Register actions
        _action_registry.register_action(
            TradeAction(trade_agent)
        )
        _action_registry.register_action(
            RebalanceAction(trade_agent, strategy_engine)
        )
        _action_registry.register_action(
            AnalyzePortfolioAction(db_manager, strategy_engine)
        )
        
    return _action_registry

def get_portfolio_agent():
    global _portfolio_agent
    if _portfolio_agent is None:
        db_manager = get_db_manager()
        allora_client = get_allora_client()
        strategy_engine = get_strategy_engine()
        # trade_agent = get_trade_agent()
        # _portfolio_agent = PortfolioAgent(allora_client, db_manager, strategy_engine)
        # # Add trade_agent to portfolio_agent
        # _portfolio_agent.trade_agent = trade_agent
        action_registry = get_action_registry()
        wallet_provider = get_wallet_provider()
        
        _portfolio_agent = PortfolioAgent(
            allora_client, 
            db_manager, 
            strategy_engine,
            action_registry,
            wallet_provider
        )
    return _portfolio_agent

def get_websocket_manager():
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager

def get_wallet_provider():
    global _wallet_provider
    if _wallet_provider is None:
        db_manager = get_db_manager()
        _wallet_provider = WalletProvider()
    return _wallet_provider

def get_action_providers():
    # Initialize providers with their dependencies
    db_manager = get_db_manager()
    trade_agent = get_trade_agent()
    wallet_provider = get_wallet_provider()
    
    return [
        TradeActionProvider(trade_agent, wallet_provider)
        # Add more providers as needed
    ]

def get_agent_kit():
    #  global _agent_kit
    # if _agent_kit is None:
    #     action_providers = get_action_providers()
    #     wallet_provider = get_wallet_provider()
    #     _agent_kit = AgentKit(action_providers, wallet_provider)
    # return _agent_kit
    """Get or create the agent kit instance"""
    config = get_settings()
    wallet_provider = get_wallet_provider()
    
    # Create RebalancerAgentKit with default providers
    return RebalancerAgentKit.create_with_default_providers(
        config=config,
        wallet_provider=wallet_provider
    )

def get_chat_service():
    global _chat_service
    if _chat_service is None:
        db_manager = get_db_manager()
        #portfolio_agent = get_portfolio_agent()
        agent_kit = get_agent_kit()
        websocket_manager = get_websocket_manager()
        #_chat_service = ChatService(db_manager, portfolio_agent, websocket_manager)
        _chat_service = ChatService(db_manager, agent_kit, websocket_manager)
    return _chat_service 