from typing import Dict, Any, cast, Optional
from coinbase_agentkit.action_providers.base import ActionProvider, create_action
from coinbase_agentkit.wallet_providers.base import WalletProvider
from coinbase_agentkit.network import Network

from kuru_sdk.client import KuruClient
from kuru_sdk.order_executor import OrderExecutor

from .schemas import SwapParams, LimitOrderParams
from .constants import SUPPORTED_NETWORKS

class KuruActionProvider(ActionProvider[WalletProvider]):
    """Provider for Kuru DEX actions"""
    
    def __init__(self, rpc_url_by_chain_id: Optional[Dict[int, str]] = None):
        super().__init__("kuru", SUPPORTED_NETWORKS)
        self.clients: Dict[int, KuruClient] = {}
        self.order_executors: Dict[int, OrderExecutor] = {}
        self.rpc_url_by_chain_id = rpc_url_by_chain_id or {}
    
    def supports_network(self, network: Network) -> bool:
        """Check if this provider supports the given network"""
        return network.chain_id in SUPPORTED_NETWORKS
    
    async def _ensure_client_initialized(self, wallet_provider: WalletProvider, chain_id: int) -> bool:
        """Ensure Kuru client is initialized for the given chain"""
        if chain_id in self.clients:
            return True
            
        if chain_id not in SUPPORTED_NETWORKS:
            return False
            
        wallet = await wallet_provider.get_wallet(chain_id)
        if not wallet:
            return False
            
        rpc_url = self.rpc_url_by_chain_id.get(chain_id)
        if not rpc_url:
            # Default RPC URLs could be defined in constants.py
            return False
            
        try:
            self.clients[chain_id] = KuruClient(
                rpc_url=rpc_url,
                private_key=wallet.private_key
            )
            self.order_executors[chain_id] = OrderExecutor(self.clients[chain_id])
            return True
        except Exception:
            return False
    
    @create_action(
        name="kuru-swap",
        description="Swap tokens on Kuru DEX",
        schema=SwapParams
    )
    async def swap(self, wallet_provider: WalletProvider, args: Dict[str, Any]) -> str:
        """Swap tokens on Kuru DEX"""
        # Extract parameters from args dict as per AgentKit pattern
        params = SwapParams(**args)
        chain_id = args.get("chain_id", 8453)  # Default to Base
        
        # Ensure client is initialized
        if not await self._ensure_client_initialized(wallet_provider, chain_id):
            return f"Failed to initialize Kuru client for chain {chain_id}"
        
        client = self.clients[chain_id]
        order_executor = self.order_executors[chain_id]
        
        try:
            # Calculate min amount out if not provided
            min_amount_out = params.min_amount_out
            if not min_amount_out and params.slippage_percentage is not None:
                # Get quote from Kuru
                quote = await client.get_quote(
                    from_token=params.from_token,
                    to_token=params.to_token,
                    amount=float(params.amount_in)
                )
                expected_out = float(quote['expectedOut'])
                slippage_factor = (1 - params.slippage_percentage / 100)
                min_amount_out = expected_out * slippage_factor
            
            # Execute the swap
            tx = await order_executor.execute_market_order(
                from_token=params.from_token,
                to_token=params.to_token,
                amount_in=float(params.amount_in),
                min_amount_out=float(min_amount_out) if min_amount_out else None
            )
            
            return f"Successfully executed swap on Kuru. Transaction hash: {tx.hash}"
        except Exception as e:
            return f"Failed to execute swap: {str(e)}"
    
    @create_action(
        name="kuru-limit-order",
        description="Place a limit order on Kuru DEX",
        schema=LimitOrderParams
    )
    async def place_limit_order(self, wallet_provider: WalletProvider, args: Dict[str, Any]) -> str:
        """Place a limit order on Kuru DEX"""
        params = LimitOrderParams(**args)
        chain_id = args.get("chain_id", 8453)  # Default to Base
        
        # Ensure client is initialized
        if not await self._ensure_client_initialized(wallet_provider, chain_id):
            return f"Failed to initialize Kuru client for chain {chain_id}"
        
        client = self.clients[chain_id]
        order_executor = self.order_executors[chain_id]
        
        try:
            # Place the limit order
            order_id = await order_executor.place_limit_order(
                from_token=params.from_token,
                to_token=params.to_token,
                amount=float(params.amount_in),
                price=float(params.price),
                expiry=params.expiry
            )
            
            return f"Successfully placed limit order on Kuru. Order ID: {order_id}"
        except Exception as e:
            return f"Failed to place limit order: {str(e)}"