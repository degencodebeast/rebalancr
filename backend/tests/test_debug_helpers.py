import os
import json
import asyncio
import aiohttp
import logging
from rebalancr.intelligence.agent_kit.wallet_provider import PrivyWalletProvider
from rebalancr.config import Settings

# Enhanced logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_wallet_files(wallet_provider, user_id):
    """Check if wallet files exist and show their contents"""
    path = wallet_provider._get_wallet_path(user_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            print(f"Wallet file contents: {json.dumps(data, indent=2)}")
    else:
        print(f"No wallet file found at: {path}")

async def test_network_connectivity(wallet_provider):
    """Test connectivity to the blockchain network"""
    chain_id = wallet_provider._get_chain_id_from_network_id(wallet_provider.network_id)
    rpc_url = wallet_provider._get_rpc_url_for_network(wallet_provider.network_id)
    
    print(f"Testing connectivity to: {rpc_url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            rpc_url,
            json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        ) as response:
            data = await response.json()
            print(f"Network response: {data}")
            return "result" in data

async def run_debug_tests():
    """Run all debugging tests"""
    settings = Settings()
    wallet_provider = PrivyWalletProvider.get_instance(settings)
    
    # Test user ID
    test_user_id = "test_user_123"
    
    # 1. Check network connectivity
    network_connected = await test_network_connectivity(wallet_provider)
    print(f"Network connectivity: {network_connected}")
    
    # 2. Ensure user has a wallet
    wallet_data = await wallet_provider.get_or_create_wallet(test_user_id)
    print(f"Wallet address: {wallet_data.get('address')}")
    
    # 3. Check wallet files
    check_wallet_files(wallet_provider, test_user_id)
    
    # 4. Print network settings
    network_id = wallet_provider.network_id
    chain_id = wallet_provider._get_chain_id_from_network_id(network_id)
    rpc_url = wallet_provider._get_rpc_url_for_network(network_id)
    
    print(f"Network ID: {network_id}")
    print(f"Chain ID: {chain_id}")
    print(f"RPC URL: {rpc_url}")

if __name__ == "__main__":
    asyncio.run(run_debug_tests()) 