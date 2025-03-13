from fastapi import Depends, FastAPI
import logging
from typing import List

from ..intelligence.intelligence_engine import IntelligenceEngine
from ..intelligence.market_analysis import MarketAnalyzer
from ..database.db_manager import DatabaseManager
from ..intelligence.agent_kit.service import AgentKitService
from ..intelligence.allora.client import AlloraClient
from ..strategy.engine import StrategyEngine
from ..websockets.websocket_manager import WebSocketManager, websocket_manager
from ..services.chat_service import ChatService

from ..config import get_settings
from ..intelligence.agent_kit.wallet_provider import PrivyWalletProvider, get_wallet_provider

# Chat and service imports
from ..chat.history_manager import ChatHistoryManager
from ..services.market import MarketDataService

# Strategy imports
from ..strategy.risk_manager import RiskManager
from ..strategy.yield_optimizer import YieldOptimizer
from ..strategy.wormhole import WormholeService

# Agent imports
from ..intelligence.agent_kit.agent_manager import AgentManager
from ..intelligence.agent_kit.client import AgentKitClient

# Analytics imports
from ..performance.analyzer import PerformanceAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Singletons
_db_manager = None
_allora_client = None
_strategy_engine = None
_wallet_provider = None
_chat_service = None
_action_registry = None
_agent_kit_service = None
_intelligence_engine = None
_agent_manager = None
_agent_kit_client = None
_market_analyzer = None
_market_data_service = None
_risk_manager = None
_yield_optimizer = None
_wormhole_service = None
_performance_analyzer = None

def get_db_manager():
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def get_allora_client():
    global _allora_client
    if _allora_client is None:
        config = get_settings()
        _allora_client = AlloraClient(api_key=config.ALLORA_API_KEY)
    return _allora_client

def get_strategy_engine():
    global _strategy_engine
    if _strategy_engine is None:
        _strategy_engine = StrategyEngine()
    return _strategy_engine

def get_agent_kit_service():
    """Get AgentKitService singleton instance"""
    from ..intelligence.agent_kit.service import AgentKitService
    config = get_settings()
    # Initialize without wallet_provider and agent_manager
    return AgentKitService.get_instance(config)

def get_agent_manager():
    """Get AgentManager singleton instance"""
    # Lazy import to avoid circular dependency
    from ..intelligence.agent_kit.agent_manager import AgentManager
    config = get_settings()
    return AgentManager.get_instance(config)

def get_agent_kit_client():
    """Get or create the AgentKitClient instance"""
    global _agent_kit_client
    if _agent_kit_client is None:
        config = get_settings()
        #agent_kit_service = get_agent_kit_service()
        intelligence_engine = get_intelligence_engine()
        agent_manager = get_agent_manager()
        _agent_kit_client = AgentKitClient(config, intelligence_engine, agent_manager)
    return _agent_kit_client

# def get_action_registry():
#     global _action_registry
#     if _action_registry is None:
#         _action_registry = ActionRegistry()
        
#         # Get dependencies
#         db_manager = get_db_manager()
#         strategy_engine = get_strategy_engine()
        
#         # Register actions
#         _action_registry.register_action(
#             AnalyzePortfolioAction(db_manager, strategy_engine)
#         )
        
#         # Note: TradeAction and RebalanceAction were removed as they depended on TradeAgent
#         # New action implementations should use AgentKitClient instead
        
#     return _action_registry

def get_chat_history_manager():
    """Get chat history manager instance"""
    # Directly create instance rather than using AgentManager
    from ..chat.history_manager import ChatHistoryManager
    db_manager = get_db_manager()
    return ChatHistoryManager(db_manager=db_manager)

def get_websocket_manager():
    """Get websocket manager singleton"""
    return websocket_manager  # Use the singleton from import

def get_intelligence_engine():
    """Get intelligence engine instance"""
    global _intelligence_engine
    if _intelligence_engine is None:
        # Get dependencies
        config = get_settings()
        allora_client = get_allora_client()
        market_analyzer = get_market_analyzer()
        agent_kit_client = get_agent_kit_client()
        market_data_service = get_market_data_service()
        
        _intelligence_engine = IntelligenceEngine(
            allora_client=allora_client,
            market_analyzer=market_analyzer,
            agent_kit_client=agent_kit_client,
            market_data_service=market_data_service,
            config=config
        )
    return _intelligence_engine

def get_chat_service():
    global _chat_service
    if _chat_service is None:
        # Using the AgentManager pattern for chat
        agent_manager = get_agent_manager()
        chat_history_manager = get_chat_history_manager()
        websocket_manager = get_websocket_manager()
        
        _chat_service = ChatService(
            db_manager=get_db_manager(),
            agent_manager=agent_manager,
            websocket_manager=websocket_manager
        )
    return _chat_service

def get_market_analyzer():
    global _market_analyzer
    if _market_analyzer is None:
        _market_analyzer = MarketAnalyzer()
    return _market_analyzer

def get_market_data_service():
    global _market_data_service
    if _market_data_service is None:
        config = get_settings()
        _market_data_service = MarketDataService(config)
    return _market_data_service

def get_risk_manager():
    global _risk_manager
    if _risk_manager is None:
        config = get_settings()
        db_manager = get_db_manager()
        _risk_manager = RiskManager(db_manager, config)
    return _risk_manager

def get_yield_optimizer():
    global _yield_optimizer
    if _yield_optimizer is None:
        config = get_settings()
        db_manager = get_db_manager()
        market_data_service = get_market_data_service()
        _yield_optimizer = YieldOptimizer(db_manager, market_data_service, config)
    return _yield_optimizer

def get_wormhole_service():
    global _wormhole_service
    if _wormhole_service is None:
        config = get_settings()
        _wormhole_service = WormholeService(config)
    return _wormhole_service

def get_performance_analyzer():
    global _performance_analyzer
    if _performance_analyzer is None:
        config = get_settings()
        db_manager = get_db_manager()
        _performance_analyzer = PerformanceAnalyzer(
            db_manager=db_manager,
            #config=config
        )
    return _performance_analyzer

def initialize_services(app: FastAPI):
    """Initialize all services and attach to app state"""
    # Initialize core services
    services = initialize_intelligence_services()
    
    # Attach to app state
    app.state.db_manager = get_db_manager()
    app.state.allora_client = get_allora_client()
    app.state.agent_service = services["agent_kit_service"]
    app.state.agent_manager = services["agent_manager"]
    app.state.agent_kit_client = services["agent_kit_client"]
    app.state.intelligence_engine = services["intelligence_engine"]
    app.state.market_analyzer = get_market_analyzer()
    app.state.strategy_engine = get_strategy_engine()
    app.state.market_data_service = get_market_data_service()
    app.state.risk_manager = get_risk_manager()
    app.state.yield_optimizer = get_yield_optimizer()
    app.state.chat_service = get_chat_service()
    app.state.websocket_manager = get_websocket_manager()
    app.state.wallet_provider = get_wallet_provider()
    
    return app

def initialize_intelligence_services():
    """Initialize intelligence services and providers in the correct order to avoid circular imports"""
    
    # 1. Initialize basic services 
    config = get_settings()
    allora_client = get_allora_client()
    market_analyzer = get_market_analyzer()
    market_data_service = get_market_data_service()
    db_manager = get_db_manager()
    
    # 2. Initialize wallet provider
    from ..intelligence.agent_kit.wallet_provider import PrivyWalletProvider
    wallet_provider = PrivyWalletProvider.get_instance(config)
    
    # 3. Initialize agent kit service
    from ..intelligence.agent_kit.service import AgentKitService
    agent_kit_service = AgentKitService.get_instance(config, wallet_provider=wallet_provider)
    
    # 4. Initialize agent manager
    from ..intelligence.agent_kit.agent_manager import AgentManager
    agent_manager = AgentManager.get_instance(config)
    
    # 5. Set agent manager in service
    agent_kit_service.set_agent_manager(agent_manager)
    
    # 6. Initialize agent client
    from ..intelligence.agent_kit.client import AgentKitClient
    agent_kit_client = AgentKitClient(config, agent_manager=agent_manager)
    
    # 7. Initialize strategy engine
    strategy_engine = get_strategy_engine()
    
    # 8. Initialize IntelligenceEngine
    from ..intelligence.intelligence_engine import IntelligenceEngine
    intelligence_engine = IntelligenceEngine(
        allora_client=allora_client,
        market_analyzer=market_analyzer,
        agent_kit_client=agent_kit_client,
        market_data_service=market_data_service,
        config=config,
        db_manager=db_manager,
        strategy_engine=strategy_engine
    )
    
    # 9. Connect components
    agent_kit_client.set_intelligence_engine(intelligence_engine)
    strategy_engine.set_intelligence_engine(intelligence_engine)
    
    # 10. Prepare other dependencies
    risk_manager = get_risk_manager()
    yield_optimizer = get_yield_optimizer() 
    
    try:
        performance_analyzer = get_performance_analyzer()
    except Exception as e:
        logger.warning(f"Performance analyzer not available: {e}")
        performance_analyzer = None
    
    # 11. Create action providers
    from ..execution.providers.portfolio.portfolio_action_provider import portfolio_action_provider
    portfolio_provider = portfolio_action_provider(
        wallet_provider=wallet_provider,
        intelligence_engine=intelligence_engine,
        strategy_engine=strategy_engine,
        risk_manager=risk_manager,
        yield_optimizer=yield_optimizer,
        performance_analyzer=performance_analyzer,
        db_manager=db_manager,
        config=config
    )
    
    # 12. Import rebalancer only after intelligence_engine is fully initialized
    from ..execution.providers.rebalancer.rebalancer_action_provider import rebalancer_action_provider
    from ..intelligence.reviewer import TradeReviewer

    # First, get or create a trade reviewer if needed
    trade_reviewer = TradeReviewer()

    rebalancer_provider = rebalancer_action_provider(
        wallet_provider=wallet_provider,
        intelligence_engine=intelligence_engine,
        strategy_engine=strategy_engine,
        trade_reviewer=trade_reviewer,
        performance_analyzer=performance_analyzer,
        db_manager=db_manager,
        context={"user_id": "default"},  # Add a default context
        config=config
    )
    
    # 13. Register providers with service
    agent_kit_service.register_portfolio_provider(portfolio_provider)
    agent_kit_service.register_rebalancer_provider(rebalancer_provider)
    
    # 14. Update action providers in agent manager
    agent_manager.set_action_providers(agent_kit_service.get_action_providers())
    
    # 15. Return initialized services
    return {
        "intelligence_engine": intelligence_engine,
        "agent_kit_client": agent_kit_client,
        "agent_kit_service": agent_kit_service,
        "agent_manager": agent_manager,
        "portfolio_provider": portfolio_provider,
        "rebalancer_provider": rebalancer_provider
    }