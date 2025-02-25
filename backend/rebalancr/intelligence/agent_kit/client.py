from coinbase_agentkit import AgentKit
import asyncio

class AgentKitClient:
    def __init__(self, config):
        self.agent_kit = AgentKit(
            agent_id=config.AGENT_ID,
            api_key=config.API_KEY,
            api_secret=config.API_SECRET
        )
        self.conversations = {}  # Store active conversations
        
    async def initialize_session(self, user_id):
        """Initialize a new conversation for a user"""
        conversation = await self.agent_kit.create_conversation(user_id)
        self.conversations[user_id] = conversation.id
        return conversation.id
        
    async def send_message(self, user_id, message):
        """Send a message to the agent"""
        if user_id not in self.conversations:
            await self.initialize_session(user_id)
            
        return await self.agent_kit.send_message(
            conversation_id=self.conversations[user_id],
            content=message
        )
    
    async def execute_smart_contract(self, user_id, contract_address, function_name, args):
        """Execute a smart contract call via AgentKit"""
        if user_id not in self.conversations:
            await self.initialize_session(user_id)
            
        return await self.agent_kit.smart_contract_write(
            conversation_id=self.conversations[user_id],
            contract_address=contract_address,
            function_name=function_name,
            args=args
        )
        
    async def check_curvance_delegation(self, user_id, plugin_address):
        """Check if user has delegated to our plugin"""
        if user_id not in self.conversations:
            await self.initialize_session(user_id)
            
        # Get user's wallet address
        user_info = await self.agent_kit.get_user_info(self.conversations[user_id])
        wallet_address = user_info.wallet_address
        
        # Call curvance contract to check delegation
        result = await self.agent_kit.smart_contract_read(
            conversation_id=self.conversations[user_id],
            contract_address="CURVANCE_CONTROLLER_ADDRESS",
            function_name="checkDelegateApproval",
            args=[wallet_address, plugin_address]
        )
        
        return result
