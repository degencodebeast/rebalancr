import asyncio
import time
import json
from rebalancr.intelligence.agent_kit.wallet_provider import PrivyWalletProvider
from rebalancr.config import Settings

async def test_wallet_methods():
    settings = Settings()
    wallet_provider = PrivyWalletProvider.get_instance(settings)
    
    # Test cases with results
    results = {}
    
    # 1. Test wallet creation
    test_user_id = f"test_user_{int(time.time())}"  # Unique ID
    results["create_wallet"] = await wallet_provider.create_wallet(test_user_id)
    
    # 2. Test signature
    message = "Test message for signing"
    results["sign_message"] = await wallet_provider.sign_message(message)
    
    # 3. Test transaction preparation
    tx = {
        "to": "0x0000000000000000000000000000000000000000",
        "value": 0,
        "data": "0x"
    }
    results["prepare_tx"] = wallet_provider._prepare_transaction(tx)
    
    # 4. Test wallet export
    results["export_wallet"] = wallet_provider.export_wallet()
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_wallet_methods())
    
    # Pretty print results
    print(json.dumps(results, indent=2)) 