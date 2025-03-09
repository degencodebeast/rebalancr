from fastapi import WebSocket, WebSocketDisconnect, status
from ..auth.wallet import verify_auth_token
import jwt
from jwt import PyJWTError
import logging
import json
from ..config import get_settings

logger = logging.getLogger(__name__)

async def verify_privy_token(token: str, expected_user_id: str = None) -> dict:
    """
    Verify a Privy authentication token
    
    Args:
        token: Privy JWT token
        expected_user_id: Optional user ID to validate against
        
    Returns:
        Dict with validation result
    """
    config = get_settings()
    try:
        # Verify JWT (in production, you should verify the signature with Privy's public key)
        # For now, we're just decoding to extract claims
        decoded = jwt.decode(
            token, 
            options={"verify_signature": False}  # In production, set to True with proper key
        )
        
        # Verify issuer and audience
        if decoded.get('iss') != 'privy.io':
            return {"is_valid": False, "error": "Invalid token issuer"}
        
        if decoded.get('aud') != config.PRIVY_APP_ID:
            return {"is_valid": False, "error": "Invalid token audience"}
            
        # Get the user's Privy DID from the subject claim
        user_id = decoded.get('sub')
        
        # If expected_user_id is provided, verify it matches
        if expected_user_id and user_id != expected_user_id:
            return {"is_valid": False, "error": "User ID mismatch"}
            
        return {"is_valid": True, "user_id": user_id}
    except PyJWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        return {"is_valid": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return {"is_valid": False, "error": str(e)}

async def authenticate_websocket(websocket: WebSocket) -> dict:
    """
    Authenticate a WebSocket connection using Privy
    
    Args:
        websocket: WebSocket connection
        
    Returns:
        Dict with authentication result and user_id
    """
    try:
        # Wait for auth message
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        
        # Check if auth data has token
        if "type" not in auth_data or auth_data["type"] != "auth":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return {"success": False, "error": "Invalid auth message"}
        
        if "token" not in auth_data:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return {"success": False, "error": "Missing auth token"}
        
        # Verify token
        token_result = await verify_privy_token(auth_data["token"])
        if not token_result["is_valid"]:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return {"success": False, "error": token_result.get("error")}
        
        # Return user ID from token
        return {
            "success": True,
            "user_id": token_result["user_id"]
        }
    except WebSocketDisconnect:
        return {"success": False, "error": "Client disconnected during authentication"}
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return {"success": False, "error": str(e)}
