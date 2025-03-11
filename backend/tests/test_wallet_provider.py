import asyncio
import logging
from rebalancr.intelligence.agent_kit.wallet_provider import PrivyWalletProvider
from rebalancr.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_wallet_provider():
    """Test basic wallet provider functionality"""
    # 1. Initialize settings
    settings = Settings()
    
    # 2. Get wallet provider instance
    wallet_provider = PrivyWalletProvider.get_instance(settings)
    logger.info("Wallet provider initialized")
    
    # 3. Test user wallet creation and retrieval
    test_user_id = "test_user_123"
    logger.info(f"Testing wallet creation for user: {test_user_id}")
    
    wallet_data = await wallet_provider.get_or_create_wallet(test_user_id)
    logger.info(f"Wallet created/retrieved: {wallet_data.get('address')}")
    
    # 4. Check wallet balance
    balance = wallet_provider.get_balance()
    logger.info(f"Wallet balance: {balance}")
    
    # 5. Test wallet address retrieval
    address = wallet_provider.get_address()
    logger.info(f"Wallet address: {address}")
    
    # 6. Test network retrieval
    network = wallet_provider.get_network()
    logger.info(f"Network: {network}")
    
    return {
        "success": True,
        "address": address,
        "balance": balance,
        "network": network
    }

if __name__ == "__main__":
    result = asyncio.run(test_wallet_provider())
    logger.info(f"Test completed: {result}") 