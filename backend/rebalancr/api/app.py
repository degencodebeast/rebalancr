from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
import logging
import asyncio

from ..database.db_manager import DatabaseManager
from ..intelligence.agent_kit.wallet_provider import get_wallet_provider
from ..intelligence.agent_kit.chat_agent import PortfolioAgent
from ..intelligence.allora.client import AlloraClient
from ..chat.history_manager import ChatHistoryManager
from .websocket import connection_manager
from ..websockets.chat_handler import ChatWebSocketHandler
from ..config import Config
from ..intelligence.market_data import MarketDataService
from ..strategy.risk_manager import RiskManager
from ..strategy.yield_optimizer import YieldOptimizer
from ..strategy.wormhole import WormholeService
from ..strategy.engine import StrategyEngine
from ..intelligence.intelligence_engine import IntelligenceEngine
from ..intelligence.market_analysis import MarketAnalyzer
from ..intelligence.agent_kit.client import AgentKitClient
from ..services.chat import ChatService
from coinbase_agentkit import AgentKit, AgentKitConfig
from ..intelligence.agent_kit.trade_agent import TradeAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = Config()

# Initialize application
app = FastAPI(title="Rebalancr API")

# Initialize database
db_manager = DatabaseManager(config.DATABASE_URL)

# Initialize Allora client
allora_client = AlloraClient(api_key=config.ALLORA_API_KEY)

# Initialize market analyzer and agent kit client
market_analyzer = MarketAnalyzer()
agent_kit_client = AgentKitClient(config)

# Initialize wallet provider
#wallet_provider = get_wallet_provider(config)
wallet_provider = get_wallet_provider()

# Initialize AgentKit with the Privy wallet provider
agentkit = AgentKit(AgentKitConfig(
    wallet_provider=wallet_provider,
    action_providers=[
        # Your action providers here
    ]
))

# Initialize missing components
market_data_service = MarketDataService(config)
risk_manager = RiskManager(config)
yield_optimizer = YieldOptimizer(config)
wormhole_service = WormholeService(config)

# Initialize intelligence engine
intelligence_engine = IntelligenceEngine(
    allora_client=allora_client,
    market_analyzer=market_analyzer,
    agent_kit_client=agent_kit_client,
    market_data_service=market_data_service,
    config=config
)

# Now initialize strategy engine with all components
strategy_engine = StrategyEngine(
    intelligence_engine=intelligence_engine,
    risk_manager=risk_manager,
    yield_optimizer=yield_optimizer,
    wormhole_service=wormhole_service,
    db_manager=db_manager,
    config=config
)


# Initialize agent
# portfolio_agent = PortfolioAgent(
#     allora_client=allora_client,
#     wallet_provider=wallet_provider,
#     config={
#         "model": config.LLM_MODEL,
#         "wallet_data_file": "wallet_data.json"
#     }
# )
trade_agent = TradeAgent(db_manager, market_analyzer, wallet_provider)
portfolio_agent = PortfolioAgent(allora_client, db_manager, strategy_engine, trade_agent)

# Initialize chat history manager
chat_history_manager = ChatHistoryManager(db_manager=db_manager)

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


# Portfolio monitoring function
async def monitor_portfolios():
    """Background task to monitor portfolios and trigger rebalancing when needed"""
    while True:
        try:
            # Get all active portfolios
            active_portfolios = await db_manager.get_active_portfolios()
            
            for portfolio in active_portfolios:
                user_id = portfolio['user_id']
                portfolio_id = portfolio['id']
                
                # Check if portfolio needs rebalancing
                analysis = await strategy_engine.analyze_rebalance_opportunity(user_id, portfolio_id)
                
                if analysis.get("rebalance_recommended", False):
                    # Notify user that rebalancing is recommended
                    await connection_manager.send_personal_message(
                        {
                            "type": "rebalance_recommendation",
                            "portfolio_id": portfolio_id,
                            "message": analysis.get("message", "Rebalancing is recommended.")
                        },
                        user_id
                    )
            
            # Wait before next check
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            logger.error(f"Error monitoring portfolios: {str(e)}")
            await asyncio.sleep(300)  # Wait and retry

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for chat communication"""
    await connection_manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await connection_manager.send_personal_message(
            {
                "type": "system_message",
                "message": "Connected to Rebalancr chat service"
            },
            user_id
        )
        
        # Process messages
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "chat_message":
                message = data.get("message", "")
                conversation_id = data.get("conversation_id")
                
                if message:
                    # Process through the chat service
                    async for response_chunk in chat_service.process_message(
                        user_id, message, conversation_id
                    ):
                        # Send each chunk as it becomes available
                        await connection_manager.send_personal_message(
                            {
                                "type": response_chunk["type"],
                                "message": response_chunk["content"],
                                "conversation_id": response_chunk["conversation_id"]
                            },
                            user_id
                        )
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {user_id}")
        connection_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"Error in websocket: {str(e)}")
        connection_manager.disconnect(websocket, user_id)

# At the end of your app initialization
@app.on_event("startup")
async def startup_event():
    # Start portfolio monitoring in background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(monitor_portfolios)

# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, Query
# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional, Dict, List
# import json

# from rebalancr.api.websocket import connection_manager
# # from rebalancr.services.chat import ChatService
# # from rebalancr.services.portfolio import PortfolioService
# # from rebalancr.services.user import UserService
# # from rebalancr.services.market import MarketService

# from rebalancr.intelligence.allora.client import AlloraClient
# from rebalancr.intelligence.market_analysis import MarketAnalyzer
# from rebalancr.intelligence.agent_kit.client import AgentKitClient
# from rebalancr.intelligence.market_data import MarketDataService
# from rebalancr.intelligence.strategy_engine import StrategyEngine
# from rebalancr.api.websocket_handlers import ChatWebSocketHandler
# from rebalancr.config import Config
# from ..db.manager import DatabaseManager
# from ..intelligence.agent_kit.wallet_provider import get_wallet_provider
# from ..intelligence.agent_kit.chat_agent import PortfolioAgent
# from ..chat.history_manager import ChatHistoryManager

# # Import all route modules
# # from rebalancr.api.routes import portfolio, market, chat, user, social, achievement

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI(
#     title="Rebalancr API",
#     description="Portfolio rebalancing and market analysis API",
#     version="0.1.0"
# )

# # Configure CORS
# origins = [
#     "http://localhost:3000",  # Next.js default port
#     "http://localhost:8000",
#     "http://localhost",
#     # Add your production domains when deploying
# ]

# app.add_middleware(
#     CORSMiddleware,
#     #allow_origins=["*"], // for testing, to allow all origins
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # chat_service = ChatService()
# # portfolio_service = PortfolioService()
# # user_service = UserService()
# # market_service = MarketService()

# # Initialize services
# config = Config()

# # Initialize database
# db_manager = DatabaseManager(config.DATABASE_URL)

# # Initialize Allora client
# allora_client = AlloraClient(api_key=config.ALLORA_API_KEY)

# # market_analyzer = MarketAnalyzer()
# # agent_kit_client = AgentKitClient(config)
# # market_data_service = MarketDataService()

# # # Strategy engine with dual approach (Rose Heart's advice)
# # strategy_engine = StrategyEngine()


# # Initialize wallet provider
# wallet_provider = get_wallet_provider(config)

# # Initialize agent
# portfolio_agent = PortfolioAgent(
#     allora_client=allora_client,
#     # market_analyzer=market_analyzer,
#     # agent_kit_client=agent_kit_client,
#     # market_data_service=market_data_service,
#     # config=config
#     wallet_provider=wallet_provider,
#     config={
#         "model": config.LLM_MODEL,
#         "wallet_data_file": "wallet_data.json"
#     }
# )

# # # Auth dependency - simplified for hackathon
# # async def get_user_from_token(token: str = Query(...)):
# #     # In a real app, validate the token against your database
# #     # For hackathon, just extract user_id from token directly
# #     return token

# # Initialize chat history manager
# chat_history_manager = ChatHistoryManager(db_manager=db_manager)

# # Include all routers
# # app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
# # app.include_router(market.router, prefix="/api/market", tags=["Market"])
# # app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# # app.include_router(user.router, prefix="/api/user", tags=["User"])
# # app.include_router(social.router, prefix="/api/social", tags=["Social"])
# # app.include_router(achievement.router, prefix="/api/achievement", tags=["Achievement"])

# # WebSocket handler

# # Initialize WebSocket handler
# chat_ws_handler = ChatWebSocketHandler(
#     # strategy_engine=strategy_engine,
#     # agent_kit_client=agent_kit_client
#     portfolio_agent=portfolio_agent,
#     chat_history_manager=chat_history_manager
# )

# # WebSocket Authentication
# async def get_token(
#     websocket: WebSocket,
#     token: Optional[str] = Query(None),
#     authorization: Optional[str] = Header(None)
# ) -> str:
#     # Extract token from Query param or Authorization header
#     if token:
#         return token
#     elif authorization and authorization.startswith("Bearer "):
#         return authorization.replace("Bearer ", "")
#     else:
#         await websocket.close(code=1008)  # Policy violation
#         return None


# # @app.websocket("/ws/chat")
# # async def websocket_chat_endpoint(

# # WebSocket topic subscription handler
# @app.websocket("/ws")
# # async def websocket_endpoint(
# #     websocket: WebSocket, 
# #     #user_id: str = Depends(get_user_from_token)
# #     token: str = Depends(get_token)
# # ):
# #     # Validate token and get user ID
# #     try:
# #         user_id = await user_service.validate_token(token)
# #         if not user_id:
# #             await websocket.close(code=1008)
# #             return
# #     except Exception as e:
# #         print(f"WebSocket authentication error: {str(e)}")
# #         await websocket.close(code=1008)
# #         return

# #     # Accept the connection
# async def websocket_endpoint(websocket: WebSocket):
#     # Accept connection without auth for now
#     user_id = "test_user"  # Hardcoded for testing
    
#     # Accept the connection immediately
#     await connection_manager.connect(websocket, user_id)
    
#     try:
#         ## Handle initial setup message to subscribe to topics
#         # Handle messages
#         while True:
#              # data = await websocket.receive_text()
#             # message_data = json.loads(data)
#             data = await websocket.receive_json()
#               # Process message with chat service
#               #response = await chat_service.process_message(user_id, message_data.get("message", ""))
            
#             message_type = data.get("type", "")
#             print(f"Received message of type: {message_type}")

# #                   # Send response back to this user
# # #             await connection_manager.send_personal_message(
# # #                 {"type": "chat_response", "data": response},
# # #                 user_id
# # #             )
# # #     except WebSocketDisconnect:
# # #         connection_manager.disconnect(websocket, user_id)
# # #         await connection_manager.broadcast(
# # #             {"type": "system", "data": f"User #{user_id} left the chat"}
# # #         )
# # #     except Exception as e:
# # #         print(f"Error in chat websocket: {str(e)}")
# # #         connection_manager.disconnect(websocket, user_id)

# # # @app.websocket("/ws/portfolio-updates")
# # # async def websocket_portfolio_updates(
# # #     websocket: WebSocket,
# # #     user_id: str = Depends(get_user_from_token)
# # # ):
# # #     portfolio_service = PortfolioService()
# # #     await connection_manager.connect(websocket, user_id)
# # #     try:
# # #         while True:
# # #             # Instead of waiting for client messages, this could periodically 
# # #             # push portfolio updates, but for the demo we'll wait for client pings
# # #             data = await websocket.receive_text()
            
# # #             # Get latest portfolio data
# # #             portfolio = await portfolio_service.get_portfolio(user_id)
            
# #             #  # Send updates back to the client
# #             # await connection_manager.send_personal_message(
# #             #     {"type": "portfolio_update", "data": portfolio},
# #             #     user_id
# #             # )
            
#             # Handle subscription message
#             if data.get("type") == "subscribe":
#                 topics = data.get("topics", [])
#                 # Here you would store user's topic subscriptions
#                 # For demo purposes, just acknowledge
#                 await connection_manager.send_personal_message(
#                     {"type": "subscribed", "topics": topics},
#                     user_id
#                 )
            
#             # Handle portfolio update request
#             elif data.get("type") == "get_portfolio":
#                 # Get latest portfolio data
#                 portfolio = await portfolio_service.get_portfolio(user_id)
                
#                 # Send updates back to the client
#                 await connection_manager.send_personal_message(
#                     {"type": "portfolio_update", "data": portfolio},
#                     user_id
#                 )
            
#             # Echo back the message for testing
#             await connection_manager.send_personal_message(
#                 {"type": "echo", "data": data},
#                 user_id
#             )

#             #   # Handle chat messages
#             # elif data.get("type") == "chat_message":
#             #     message = data.get("message", "")
#             #     if message:
#             #         # Process message with chat service
#             #         response = await chat_service.process_message(user_id, message)
                    
#             #         # Send response back
#             #         await connection_manager.send_personal_message(
#             #             {"type": "chat_response", "data": response},
#             #             user_id
#             #         )
            
#             # # Handle other message types as needed

#             #print(f"WebSocket error for user {user_id}: {str(e)}")
            
#             # Handle specific message types if needed
#             if message_type == "get_portfolio":
#                 # Send dummy portfolio data for testing
#                 await connection_manager.send_personal_message(
#                     {
#                         "type": "portfolio_update",
#                         "data": {"assets": [{"name": "BTC", "value": 10000}]}
#                     },
#                     user_id
#                 )
#     #   # Process message with our handler
#     #         await chat_ws_handler.handle_message(websocket, user_id, data)
            
    
#     except WebSocketDisconnect:
#         logger.info(f"Client disconnected: {user_id}")
#         connection_manager.disconnect(websocket, user_id)
#     except Exception as e:
#         logger.error(f"Error in websocket: {str(e)}")
#         connection_manager.disconnect(websocket, user_id)

@app.get("/")
async def home():
    return {
        "name": "Rebalancr API",
        "status": "online",
        "version": "0.1.0",
        "docs": "/docs"  # Link to FastAPI's automatic docs
    }
