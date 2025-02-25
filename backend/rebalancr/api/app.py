from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List
import json

from rebalancr.api.websocket import connection_manager
# from rebalancr.services.chat import ChatService
# from rebalancr.services.portfolio import PortfolioService
# from rebalancr.services.user import UserService
# from rebalancr.services.market import MarketService

# Import all route modules
# from rebalancr.api.routes import portfolio, market, chat, user, social, achievement

app = FastAPI(
    title="Rebalancr API",
    description="Portfolio rebalancing and market analysis API",
    version="0.1.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js default port
    "http://localhost:8000",
    "http://localhost",
    # Add your production domains when deploying
]

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["*"], // for testing, to allow all origins
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# chat_service = ChatService()
# portfolio_service = PortfolioService()
# user_service = UserService()
# market_service = MarketService()

# # Auth dependency - simplified for hackathon
# async def get_user_from_token(token: str = Query(...)):
#     # In a real app, validate the token against your database
#     # For hackathon, just extract user_id from token directly
#     return token

# Include all routers
# app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
# app.include_router(market.router, prefix="/api/market", tags=["Market"])
# app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# app.include_router(user.router, prefix="/api/user", tags=["User"])
# app.include_router(social.router, prefix="/api/social", tags=["Social"])
# app.include_router(achievement.router, prefix="/api/achievement", tags=["Achievement"])

# WebSocket Authentication
async def get_token(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
) -> str:
    # Extract token from Query param or Authorization header
    if token:
        return token
    elif authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    else:
        await websocket.close(code=1008)  # Policy violation
        return None


# @app.websocket("/ws/chat")
# async def websocket_chat_endpoint(

# WebSocket topic subscription handler
@app.websocket("/ws")
# async def websocket_endpoint(
#     websocket: WebSocket, 
#     #user_id: str = Depends(get_user_from_token)
#     token: str = Depends(get_token)
# ):
#     # Validate token and get user ID
#     try:
#         user_id = await user_service.validate_token(token)
#         if not user_id:
#             await websocket.close(code=1008)
#             return
#     except Exception as e:
#         print(f"WebSocket authentication error: {str(e)}")
#         await websocket.close(code=1008)
#         return

#     # Accept the connection
async def websocket_endpoint(websocket: WebSocket):
    # Accept connection without auth
    user_id = "test_user"  # Hardcoded for testing
    
    # Accept the connection immediately
    await connection_manager.connect(websocket, user_id)
    
    try:
        ## Handle initial setup message to subscribe to topics
        # Handle messages
        while True:
             # data = await websocket.receive_text()
            # message_data = json.loads(data)
            data = await websocket.receive_json()
              # Process message with chat service
              #response = await chat_service.process_message(user_id, message_data.get("message", ""))
            
            message_type = data.get("type", "")
            print(f"Received message of type: {message_type}")

#                   # Send response back to this user
# #             await connection_manager.send_personal_message(
# #                 {"type": "chat_response", "data": response},
# #                 user_id
# #             )
# #     except WebSocketDisconnect:
# #         connection_manager.disconnect(websocket, user_id)
# #         await connection_manager.broadcast(
# #             {"type": "system", "data": f"User #{user_id} left the chat"}
# #         )
# #     except Exception as e:
# #         print(f"Error in chat websocket: {str(e)}")
# #         connection_manager.disconnect(websocket, user_id)

# # @app.websocket("/ws/portfolio-updates")
# # async def websocket_portfolio_updates(
# #     websocket: WebSocket,
# #     user_id: str = Depends(get_user_from_token)
# # ):
# #     portfolio_service = PortfolioService()
# #     await connection_manager.connect(websocket, user_id)
# #     try:
# #         while True:
# #             # Instead of waiting for client messages, this could periodically 
# #             # push portfolio updates, but for the demo we'll wait for client pings
# #             data = await websocket.receive_text()
            
# #             # Get latest portfolio data
# #             portfolio = await portfolio_service.get_portfolio(user_id)
            
#             #  # Send updates back to the client
#             # await connection_manager.send_personal_message(
#             #     {"type": "portfolio_update", "data": portfolio},
#             #     user_id
#             # )
            
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
            
            # Echo back the message for testing
            await connection_manager.send_personal_message(
                {"type": "echo", "data": data},
                user_id
            )

            #   # Handle chat messages
            # elif data.get("type") == "chat_message":
            #     message = data.get("message", "")
            #     if message:
            #         # Process message with chat service
            #         response = await chat_service.process_message(user_id, message)
                    
            #         # Send response back
            #         await connection_manager.send_personal_message(
            #             {"type": "chat_response", "data": response},
            #             user_id
            #         )
            
            # # Handle other message types as needed

            #print(f"WebSocket error for user {user_id}: {str(e)}")
            
            # Handle specific message types if needed
            if message_type == "get_portfolio":
                # Send dummy portfolio data for testing
                await connection_manager.send_personal_message(
                    {
                        "type": "portfolio_update",
                        "data": {"assets": [{"name": "BTC", "value": 10000}]}
                    },
                    user_id
                )
    
    except WebSocketDisconnect:
        print(f"Client disconnected")
        connection_manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"Error in websocket: {str(e)}")
        connection_manager.disconnect(websocket, user_id)

@app.get("/")
async def home():
    return {
        "name": "Rebalancr API",
        "status": "online",
        "version": "0.1.0",
        "docs": "/docs"  # Link to FastAPI's automatic docs
    }
