import asyncio
from decimal import Decimal
from rebalancr.intelligence.agent_kit.wallet_provider import PrivyWalletProvider
from rebalancr.config import Settings

async def test_transaction():
    settings = Settings()
    wallet_provider = PrivyWalletProvider.get_instance(settings)
    
    # Get user wallet
    test_user_id = "test_user_123"
    await wallet_provider.get_or_create_wallet(test_user_id)
    
    # Check initial balance
    initial_balance = wallet_provider.get_balance()
    print(f"Initial balance: {initial_balance}")
    
    # Send a small amount to a test address (zero address for testing)
    test_address = "0x0000000000000000000000000000000000000001"
    amount = Decimal("0.0001")  # Very small amount
    
    try:
        # Execute transfer
        tx_hash = wallet_provider.native_transfer(test_address, amount)
        print(f"Transaction sent: {tx_hash}")
        
        # Wait for receipt
        receipt = wallet_provider.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction receipt: {receipt}")
        
        # Check new balance
        new_balance = wallet_provider.get_balance()
        print(f"New balance: {new_balance}")
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "initial_balance": str(initial_balance),
            "new_balance": str(new_balance)
        }
    except Exception as e:
        print(f"Transaction failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = asyncio.run(test_transaction())
    print(result) 