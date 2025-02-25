from rebalancr.intelligence.agent_kit.client import AgentKitClient
from rebalancr.api.websocket import connection_manager

class ChatService:
    def __init__(self, config, db_session):
        self.db = db_session
        self.agent_kit_client = AgentKitClient(config)
        
    async def process_message(self, user_id, message):
        # Get or create conversation
        conversation = await self.get_conversation(user_id)
        
        # Process message through AgentKit
        response = await self.agent_kit_client.agent_kit.send_message(
            conversation_id=conversation.id,
            content=message
        )
        
        # Handle any intents that were triggered
        if response.get('intents'):
            await self.handle_intents(user_id, response['intents'])
            
        # Notify user about response
        await connection_manager.send_personal_message(
            {"type": "chat_response", "data": response},
            user_id
        )
        
        return response

    async def notify_new_strategy(self, user_id, strategy):
        """Notify user about a new strategy recommendation"""
        await connection_manager.send_personal_message(
            {
                "type": "strategy_recommendation",
                "data": strategy
            },
            user_id
        )
