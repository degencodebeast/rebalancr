from fastapi import Depends, FastAPI
from rebalancr.intelligence.agent_kit.wallet_provider import get_wallet_provider
import logging

from rebalancr.websockets.chat_handler import ChatWebSocketHandler

from ..intelligence.intelligence_engine import IntelligenceEngine
from ..intelligence.market_analysis import MarketAnalyzer
from ..database.db_manager import DatabaseManager
from ..intelligence.agent_kit.service import AgentKitService
from ..intelligence.agent_kit.chat_agent import PortfolioAgent
from ..intelligence.agent_kit.trade_agent import TradeAgent
from ..intelligence.allora.client import AlloraClient
from ..strategy.engine import StrategyEngine
from ..websockets.websocket_manager import WebSocketManager
from .services.chat_service import ChatService
from ..execution.action_registry import ActionRegistry
from ..execution.actions.trade_actions import TradeAction, RebalanceAction
from ..execution.actions.portfolio_actions import AnalyzePortfolioAction
from ..agent.agent_kit import RebalancerAgentKit
from ..config import get_settings
from ..intelligence.agent_kit.wallet_provider import WalletProvider
from ..execution.action_provider import TradeActionProvider

# Chat and service imports
from ..chat.history_manager import ChatHistoryManager
from ..services.market import MarketDataService
from ..services.chat import ChatService

# Strategy imports
from ..strategy.risk_manager import RiskManager
from ..strategy.yield_optimizer import YieldOptimizer
from ..strategy.wormhole import WormholeService


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

def initialize_services(app: FastAPI):
    """Initialize all services and attach to app state"""
    # Load configuration
    config = get_settings()
    
    # Initialize database
    db_manager = DatabaseManager(config.DATABASE_URL)

    
    # Initialize Allora client
    allora_client = AlloraClient(api_key=config.ALLORA_API_KEY)
    
    # Initialize market analyzer
    market_analyzer = MarketAnalyzer()
    
    # Initialize AgentKit service (singleton)
    agent_service = AgentKitService.get_instance(config)

    wallet_provider = agent_service.wallet_provider
    
    # Initialize missing components
    market_data_service = MarketDataService(config)
    risk_manager = RiskManager(db_manager, config)
    yield_optimizer = YieldOptimizer(db_manager, market_data_service, config)
    wormhole_service = WormholeService(config)
    
    # Initialize intelligence engine
    intelligence_engine = IntelligenceEngine(
        allora_client=allora_client,
        market_analyzer=market_analyzer,
        agent_kit_service=agent_service,
        market_data_service=market_data_service,
        config=config
    )
    
    # Initialize strategy engine
    strategy_engine = StrategyEngine()

    # Initialize action registry and portfolio agent
    action_registry = ActionRegistry()
    trade_agent = TradeAgent(db_manager, market_analyzer, agent_service)
    portfolio_agent = PortfolioAgent(allora_client, db_manager, strategy_engine, config, action_registry)

    
    # Initialize chat history manager
    chat_history_manager = ChatHistoryManager(db_manager=db_manager)
    
    # Initialize WebSocket manager
    websocket_manager = get_websocket_manager()
    
    # Initialize chat service
    chat_service = ChatService(
        portfolio_agent=portfolio_agent,
        chat_history_manager=chat_history_manager
    )
    
    # Initialize WebSocket handler
    chat_ws_handler = ChatWebSocketHandler(
        portfolio_agent=portfolio_agent,
        chat_history_manager=chat_history_manager
    )
    
    # Store all services in app state for access in route handlers
    app.state.db_manager = db_manager
    app.state.allora_client = allora_client
    app.state.agent_service = agent_service
    app.state.market_analyzer = market_analyzer
    app.state.intelligence_engine = intelligence_engine
    app.state.strategy_engine = strategy_engine
    app.state.portfolio_agent = portfolio_agent
    app.state.chat_service = chat_service
    app.state.chat_ws_handler = chat_ws_handler
    app.state.websocket_manager = websocket_manager
    
    return app