from fastapi import APIRouter, WebSocket, Depends, HTTPException
from typing import Dict, Any

from ...api.websocket import connection_manager
from ...agent.agent_kit import RebalancerAgentKit
from ...api.dependencies import get_agent_kit
from ...config import get_settings

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        print("WebSocket connection accepted")
        
        # Add the minimal possible logic to test the connection
        await websocket.send_json({"type": "connection_established", "message": "Connected to server"})
        
        while True:
            try:
                data = await websocket.receive_text()
                print(f"Received: {data}")
                
                # Echo the message back as a simple test
                await websocket.send_json({
                    "type": "echo", 
                    "message": f"Echo: {data}"
                })
            except Exception as e:
                print(f"Error processing message: {e}")
                break
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    agent_kit: RebalancerAgentKit = Depends(get_agent_kit)
):
    # Accept connection
    await connection_manager.connect(websocket, user_id)
    
    try:
        # Send a welcome message
        await connection_manager.send_personal_message(
            {
                "type": "agent_response",
                "message_id": "welcome",
                "message": "Hello! I'm your Rebalancr agent. How can I help you with your portfolio today?"
            },
            user_id
        )
        
        # Process incoming messages
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data["type"] == "chat_message":
                # Acknowledge receipt
                await connection_manager.send_personal_message(
                    {"type": "message_received", "message_id": f"receipt-{user_id}"}, 
                    user_id
                )
                
                # Process message with agent
                async for chunk in agent_kit.process_message(user_id, data["message"]):
                    # Send each chunk to the user
                    chunk["message_id"] = f"response-{id(chunk)}"
                    await connection_manager.send_personal_message(chunk, user_id)
                    
            elif data["type"] == "load_history":
                # You could implement history loading here
                pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect when done
        connection_manager.disconnect(websocket, user_id) 