import asyncio
import logging
from rebalancr.intelligence.agent_kit.agent_manager import AgentManager
from rebalancr.intelligence.agent_kit.service import AgentKitService
from rebalancr.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent_with_wallet():
    """Test agent with wallet provider integration"""
    # 1. Initialize settings
    settings = Settings()
    
    # 2. Get service and agent manager instances
    service = AgentKitService.get_instance(settings)
    agent_manager = AgentManager.get_instance(settings)
    
    # 3. Test user ID
    test_user_id = "test_user_123"
    
    # 4. Create agent with wallet
    logger.info(f"Creating agent for user: {test_user_id}")
    async with agent_manager.get_agent_executor(test_user_id) as agent:
        # 5. Test wallet functionality through agent
        wallet_query = await agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": "What is my wallet address?"
            }]
        })
        
        logger.info(f"Agent wallet response: {wallet_query}")
        
        # 6. Try a basic balance query
        balance_query = await agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": "What is my wallet balance?"
            }]
        })
        
        logger.info(f"Agent balance response: {balance_query}")
    
    return {
        "success": True,
        "wallet_query": wallet_query,
        "balance_query": balance_query
    }

if __name__ == "__main__":
    result = asyncio.run(test_agent_with_wallet())
    logger.info(f"Test completed: {result}") 