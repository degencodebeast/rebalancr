from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, Query
from typing import Optional
import json

from rebalancr.api.websocket import connection_manager
from rebalancr.services.chat import ChatService
from rebalancr.services.portfolio import PortfolioService
# Import other services as needed

app = FastAPI()

# Include your REST API routes
from rebalancr.api.routes import chat, user, portfolio, social, achievement
app.include_router(chat.router)
app.include_router(user.router)
app.include_router(portfolio.router)
app.include_router(social.router)
app.include_router(achievement.router)

# Auth dependency - simplified for hackathon
async def get_user_from_token(token: str = Query(...)):
    # In a real app, validate the token against your database
    # For hackathon, just extract user_id from token directly
    return token

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket, 
    user_id: str = Depends(get_user_from_token)
):
    chat_service = ChatService()
    await connection_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message with chat service
            response = await chat_service.process_message(user_id, message_data.get("message", ""))
            
            # Send response back to this user
            await connection_manager.send_personal_message(
                {"type": "chat_response", "data": response},
                user_id
            )
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id)
        await connection_manager.broadcast(
            {"type": "system", "data": f"User #{user_id} left the chat"}
        )
    except Exception as e:
        print(f"Error in chat websocket: {str(e)}")
        connection_manager.disconnect(websocket, user_id)

@app.websocket("/ws/portfolio-updates")
async def websocket_portfolio_updates(
    websocket: WebSocket,
    user_id: str = Depends(get_user_from_token)
):
    portfolio_service = PortfolioService()
    await connection_manager.connect(websocket, user_id)
    try:
        while True:
            # Instead of waiting for client messages, this could periodically 
            # push portfolio updates, but for the demo we'll wait for client pings
            data = await websocket.receive_text()
            
            # Get latest portfolio data
            portfolio = await portfolio_service.get_portfolio(user_id)
            
            # Send updates back to the client
            await connection_manager.send_personal_message(
                {"type": "portfolio_update", "data": portfolio},
                user_id
            )
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id)
