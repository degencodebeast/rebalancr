"""Kuru DEX action provider using direct contract interactions."""

import json
import os
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from web3 import Web3
from web3.types import Wei

from coinbase_agentkit.action_providers.action_decorator import create_action
from coinbase_agentkit.action_providers.action_provider import ActionProvider
from coinbase_agentkit.network import Network
from coinbase_agentkit.wallet_providers import EvmWalletProvider

from .schemas import SwapParams, LimitOrderParams, OrderStatusParams, BatchOrderParams, MarginActionParams, OrderbookParams
from .constants import TOKEN_ADDRESSES, DEFAULT_RPC_URLS, KURU_MARKET_ABI, KURU_ROUTER_ABI, KURU_MARGIN_ABI
from .utils import approve_token, get_token_address, format_token_amount

# Define supported networks consistently with other providers
SUPPORTED_NETWORKS = ["base-mainnet", "base-sepolia"]

# Network ID to Chain ID mapping
NETWORK_ID_TO_CHAIN_ID = {
    "base-mainnet": 8453,
    "base-sepolia": 84532
}

class KuruActionProvider(ActionProvider[EvmWalletProvider]):
    """Provides actions for interacting with Kuru DEX through direct contract calls."""

    def __init__(self, 
                 rpc_url_by_chain_id: Optional[Dict[int, str]] = None, 
                 ws_url: Optional[str] = None,
                 margin_account_by_chain: Optional[Dict[int, str]] = None,
                 kuru_router_addresses: Optional[Dict[int, str]] = None):
        super().__init__("kuru", SUPPORTED_NETWORKS)
        
        # Initialize Web3 providers dictionary
        self.web3_providers: Dict[int, Web3] = {}
        
        # Set configuration values
        self.rpc_url_by_chain_id = rpc_url_by_chain_id or DEFAULT_RPC_URLS
        self.ws_url = ws_url
        self.margin_account_by_chain = margin_account_by_chain or {}
        
        # Store Kuru router addresses
        self.kuru_router_addresses = kuru_router_addresses or {
            8453: "0x05e6f736b5dedd60693fa806ce353156a1b73cf3",  # Example address for Base Mainnet
            84532: "0x05e6f736b5dedd60693fa806ce353156a1b73cf3"  # Example address for Base Sepolia
        }
    
    def supports_network(self, network: Network) -> bool:
        """Check if this provider supports the given network"""
        return network.network_id in SUPPORTED_NETWORKS
    
    async def _initialize_web3(self, chain_id: int) -> bool:
        """Initialize Web3 provider for specified chain if not already done"""
        if chain_id in self.web3_providers:
            return True
            
        rpc_url = self.rpc_url_by_chain_id.get(chain_id)
        if not rpc_url:
            return False
            
        try:
            # Create Web3 instance
            self.web3_providers[chain_id] = Web3(Web3.HTTPProvider(rpc_url))
            return True
        except Exception as e:
            return False
    
    async def _get_margin_account(self, wallet_provider: EvmWalletProvider, chain_id: int) -> str:
        """Get margin account address for the chain, or use wallet address if not specified"""
        # Get margin account from config or use wallet address
        wallet_address = wallet_provider.get_address()
        return self.margin_account_by_chain.get(chain_id, wallet_address)
    
    async def _get_contract(self, chain_id: int, address: str, abi: List[Dict[str, Any]]) -> Any:
        """Get a contract instance using Web3"""
        # Initialize Web3 if needed
        if not await self._initialize_web3(chain_id):
            raise Exception(f"Failed to initialize Web3 for chain {chain_id}")
        
        # Get Web3 provider
        web3 = self.web3_providers[chain_id]
        
        # Create and return contract instance
        return web3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
    
        # ... previous code ...
    
    async def _create_order(self, 
                          wallet_provider: EvmWalletProvider, 
                          chain_id: int,
                          market_address: str, 
                          order_type: str, 
                          side: str, 
                          size: str, 
                          price: Optional[str] = None,
                          min_amount_out: Optional[str] = None,
                          post_only: bool = False,
                          cloid: Optional[str] = None) -> str:
        """Create an order using direct contract interaction"""
        # Get market contract
        market_contract = await self._get_contract(chain_id, market_address, KURU_MARKET_ABI)
        
        # Determine order type
        order_type_value = 0  # 0 for limit
        if order_type.lower() == "market":
            order_type_value = 1
        
        # Determine side
        side_value = 0  # 0 for buy
        if side.lower() == "sell":
            side_value = 1
        
        # Convert size and price to contract format
        size_value = Web3.to_wei(float(size), 'ether')
        price_value = Web3.to_wei(float(price) if price else 0, 'ether')
        
        # Optional parameters
        min_out = Web3.to_wei(float(min_amount_out) if min_amount_out else 0, 'ether')
        client_order_id = cloid or f"order_{market_address}_{side}_{size}"
        
        # Encode the createOrder function call
        # The exact parameters depend on the actual contract implementation
        create_order_data = market_contract.encodeABI(
            fn_name="createOrder", 
            args=[
                side_value,                # side (0=buy, 1=sell)
                price_value,               # price
                size_value,                # size
                order_type_value,          # orderType
                int(post_only),            # postOnly (0=false, 1=true)
                min_out,                   # minAmountOut
                client_order_id            # client order id
            ]
        )
        
        # Prepare transaction
        tx_params = {
            "to": market_address,
            "data": create_order_data,
            "value": 0  # No ETH value sent with tx
        }
        
        # Send transaction using wallet provider
        tx_hash = wallet_provider.send_transaction(tx_params)
        
        # Return transaction hash
        return tx_hash
    
    async def _cancel_order(self, 
                         wallet_provider: EvmWalletProvider,
                         chain_id: int,
                         market_address: str, 
                         order_id: str) -> str:
        """Cancel an order using direct contract interaction"""
        # Get market contract
        market_contract = await self._get_contract(chain_id, market_address, KURU_MARKET_ABI)
        
        # Encode the cancelOrder function call
        cancel_order_data = market_contract.encodeABI(
            fn_name="cancelOrder", 
            args=[order_id]
        )
        
        # Prepare transaction
        tx_params = {
            "to": market_address,
            "data": cancel_order_data,
            "value": 0
        }
        
        # Send transaction using wallet provider
        tx_hash = wallet_provider.send_transaction(tx_params)
        
        # Return transaction hash
        return tx_hash
    
    async def _batch_orders(self,
                         wallet_provider: EvmWalletProvider,
                         chain_id: int,
                         market_address: str,
                         orders: List[Dict[str, Any]]) -> str:
        """Submit multiple orders in a batch using direct contract interaction"""
        # Get market contract
        market_contract = await self._get_contract(chain_id, market_address, KURU_MARKET_ABI)
        
        # Prepare batch orders
        order_sides = []
        order_prices = []
        order_sizes = []
        order_types = []
        order_post_only = []
        order_min_out = []
        order_cloids = []
        
        for idx, order in enumerate(orders):
            # Determine side
            side_value = 0  # 0 for buy
            if order.get("side", "").lower() == "sell":
                side_value = 1
            order_sides.append(side_value)
            
            # Price
            price = order.get("price", "0")
            order_prices.append(Web3.to_wei(float(price), 'ether'))
            
            # Size
            size = order.get("size", "0")
            order_sizes.append(Web3.to_wei(float(size), 'ether'))
            
            # Order type
            order_type_value = 0  # 0 for limit
            if order.get("order_type", "").lower() == "market":
                order_type_value = 1
            order_types.append(order_type_value)
            
            # Post only
            post_only = 1 if order.get("post_only", False) else 0
            order_post_only.append(post_only)
            
            # Minimum amount out
            min_out = order.get("min_amount_out", "0")
            order_min_out.append(Web3.to_wei(float(min_out), 'ether'))
            
            # Client order ID
            cloid = order.get("cloid", f"batch_{market_address}_{idx}")
            order_cloids.append(cloid)
        
        # Encode the batchOrders function call
        batch_orders_data = market_contract.encodeABI(
            fn_name="batchOrders", 
            args=[
                order_sides,
                order_prices,
                order_sizes,
                order_types,
                order_post_only,
                order_min_out,
                order_cloids
            ]
        )
        
        # Prepare transaction
        tx_params = {
            "to": market_address,
            "data": batch_orders_data,
            "value": 0
        }
        
        # Send transaction using wallet provider
        tx_hash = wallet_provider.send_transaction(tx_params)
        
        # Return transaction hash
        return tx_hash

    # ... previous code ...
    
    async def _deposit_to_margin(self,
                              wallet_provider: EvmWalletProvider,
                              chain_id: int,
                              token_address: str,
                              amount: Union[int, str]) -> str:
        """Deposit tokens to margin account using direct contract interaction"""
        # Get margin account address
        margin_account = await self._get_margin_account(wallet_provider, chain_id)
        
        # Convert amount to Wei if it's not already
        amount_wei = Web3.to_wei(float(amount), 'ether') if isinstance(amount, str) else amount
        
        # First approve token transfer
        await approve_token(
            wallet_provider=wallet_provider,
            token_address=token_address,
            spender_address=margin_account,
            amount=amount_wei
        )
        
        # Get margin contract
        margin_contract = await self._get_contract(chain_id, margin_account, KURU_MARGIN_ABI)
        
        # Encode the deposit function call
        deposit_data = margin_contract.encodeABI(
            fn_name="deposit", 
            args=[token_address, amount_wei]
        )
        
        # Prepare transaction
        tx_params = {
            "to": margin_account,
            "data": deposit_data,
            "value": 0
        }
        
        # Send transaction using wallet provider
        tx_hash = wallet_provider.send_transaction(tx_params)
        
        # Return transaction hash
        return tx_hash
    
    async def _get_margin_balance(self,
                              wallet_provider: EvmWalletProvider,
                              chain_id: int,
                              token_address: str) -> int:
        """Get token balance in margin account"""
        # Get margin account address
        margin_account = await self._get_margin_account(wallet_provider, chain_id)
        
        # Get margin contract
        margin_contract = await self._get_contract(chain_id, margin_account, KURU_MARGIN_ABI)
        
        # Call balanceOf function
        balance = margin_contract.functions.tokenBalances(token_address).call()
        
        return balance

    # ... previous code ...
    
    async def _get_orderbook(self,
                          wallet_provider: EvmWalletProvider,
                          chain_id: int,
                          market_address: str) -> Dict[str, Any]:
        """Get orderbook for a market"""
        # Get market contract
        market_contract = await self._get_contract(chain_id, market_address, KURU_MARKET_ABI)
        
        # Get bids
        bids = market_contract.functions.getBids().call()
        
        # Get asks
        asks = market_contract.functions.getAsks().call()
        
        # Format orderbook
        formatted_bids = []
        for bid in bids:
            formatted_bids.append({
                "price": Web3.from_wei(bid[0], 'ether'),
                "size": Web3.from_wei(bid[1], 'ether'),
                "id": bid[2]
            })
        
        formatted_asks = []
        for ask in asks:
            formatted_asks.append({
                "price": Web3.from_wei(ask[0], 'ether'),
                "size": Web3.from_wei(ask[1], 'ether'),
                "id": ask[2]
            })
        
        # Return orderbook
        return {
            "bids": formatted_bids,
            "asks": formatted_asks
        }
    
    # ... previous code ...
    
    @create_action(
        name="swap",
        description="""
This tool allows swapping tokens on the Kuru DEX.
It takes:
- from_token: The address of the token to swap from
- to_token: The address of the token to swap to
- amount_in: The amount of from_token to swap in decimal units
- min_amount_out: (Optional) Minimum amount of to_token to receive
- slippage_percentage: (Optional) Slippage tolerance in percentage (default: 0.5%)
- network_id: (Optional) Network ID (default: base-mainnet)
- market_address: The address of the market to trade on

Example:
- Swap 10 USDC for ETH: from_token=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913, to_token=0x0000000000000000000000000000000000000000, amount_in=10, market_address=0x05e6f736b5dedd60693fa806ce353156a1b73cf3

Important notes:
- The amount_in is in decimal units (e.g., 1.5 ETH, not wei)
- Either specify min_amount_out or slippage_percentage, but not both
- Supported networks: base-mainnet, base-sepolia
""",
        schema=SwapParams
    )
    async def swap(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> str:
        """Swap tokens on Kuru DEX"""
        params = SwapParams(**args)
        network_id = params.network_id
        
        # Get chain id
        chain_id = NETWORK_ID_TO_CHAIN_ID.get(network_id)
        if not chain_id:
            return f"Unsupported network: {network_id}"
        
        # Initialize Web3
        if not await self._initialize_web3(chain_id):
            return f"Failed to initialize Web3 for network {network_id}"
        
        try:
            # First approve token spending if not native token
            if params.from_token != "0x0000000000000000000000000000000000000000":
                amount_wei = Web3.to_wei(float(params.amount_in), 'ether')
                await approve_token(
                    wallet_provider=wallet_provider,
                    token_address=params.from_token,
                    spender_address=params.market_address,
                    amount=amount_wei
                )
            
            # Create a market order
            tx_hash = await self._create_order(
                wallet_provider=wallet_provider,
                chain_id=chain_id,
                market_address=params.market_address,
                order_type="market",
                side="buy" if params.is_buy else "sell",
                size=str(params.amount_in),
                min_amount_out=str(params.min_amount_out) if params.min_amount_out else None,
                cloid=f"swap_{network_id}_{params.amount_in}"
            )
            
            # Wait for receipt
            receipt = wallet_provider.wait_for_transaction_receipt(tx_hash)
            
            # Check status
            if receipt['status'] == 1:
                return f"Successfully executed swap on Kuru. Transaction hash: {tx_hash}"
            else:
                return f"Swap transaction failed. Transaction hash: {tx_hash}"
            
        except Exception as e:
            return f"Failed to execute swap: {str(e)}"
    
    @create_action(
        name="place-limit-order",
        description="""
This tool allows placing a limit order on the Kuru DEX.
It takes:
- from_token: The address of the token to sell
- to_token: The address of the token to buy
- amount_in: The amount of from_token to sell in decimal units
- price: The limit price in to_token per from_token
- post_only: (Optional) Whether to make the order post-only
- network_id: (Optional) Network ID (default: base-mainnet)
- market_address: The address of the market to trade on

Example:
- Sell 10 USDC for ETH at 0.0005 ETH per USDC: from_token=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913, to_token=0x0000000000000000000000000000000000000000, amount_in=10, price=0.0005, market_address=0x05e6f736b5dedd60693fa806ce353156a1b73cf3

Important notes:
- The amount_in is in decimal units (e.g., 10 USDC, not wei)
- Price is expressed in to_token per from_token
- Supported networks: base-mainnet, base-sepolia
""",
        schema=LimitOrderParams
    )
    async def place_limit_order(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> str:
        """Place a limit order on Kuru DEX"""
        params = LimitOrderParams(**args)
        network_id = params.network_id
        
        # Get chain id
        chain_id = NETWORK_ID_TO_CHAIN_ID.get(network_id)
        if not chain_id:
            return f"Unsupported network: {network_id}"
        
        # Initialize Web3
        if not await self._initialize_web3(chain_id):
            return f"Failed to initialize Web3 for network {network_id}"
        
        try:
            # First approve token spending if not native token
            if params.from_token != "0x0000000000000000000000000000000000000000":
                amount_wei = Web3.to_wei(float(params.amount_in), 'ether')
                await approve_token(
                    wallet_provider=wallet_provider,
                    token_address=params.from_token,
                    spender_address=params.market_address,
                    amount=amount_wei
                )
            
            # Create a limit order
            tx_hash = await self._create_order(
                wallet_provider=wallet_provider,
                chain_id=chain_id,
                market_address=params.market_address,
                order_type="limit",
                side="buy" if params.is_buy else "sell",
                size=str(params.amount_in),
                price=str(params.price),
                post_only=params.post_only,
                cloid=f"limit_{network_id}_{params.amount_in}_{params.price}"
            )
            
            # Wait for receipt
            receipt = wallet_provider.wait_for_transaction_receipt(tx_hash)
            
            # Check status
            if receipt['status'] == 1:
                return f"Successfully placed limit order on Kuru. Transaction hash: {tx_hash}"
            else:
                return f"Limit order transaction failed. Transaction hash: {tx_hash}"
            
        except Exception as e:
            return f"Failed to place limit order: {str(e)}"
    
    @create_action(
        name="cancel-order",
        description="""
This tool allows cancelling an existing order on Kuru DEX.
It takes:
- order_id: The client order ID (cloid) of the order to cancel
- market_address: The address of the market
- network_id: (Optional) Network ID (default: base-mainnet)

Example:
- Cancel order with client ID 'limit_base-mainnet_10_0.0005'

Important notes:
- You can only cancel orders that you created
- Orders that are already filled cannot be cancelled
- Supported networks: base-mainnet, base-sepolia
""",
        schema=OrderStatusParams
    )
    async def cancel_order(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> str:
        """Cancel an existing order on Kuru DEX"""
        params = OrderStatusParams(**args)
        network_id = params.network_id
        
        # Get chain id
        chain_id = NETWORK_ID_TO_CHAIN_ID.get(network_id)
        if not chain_id:
            return f"Unsupported network: {network_id}"
        
        # Initialize Web3
        if not await self._initialize_web3(chain_id):
            return f"Failed to initialize Web3 for network {network_id}"
        
        try:
            # Cancel the order
            tx_hash = await self._cancel_order(
                wallet_provider=wallet_provider,
                chain_id=chain_id,
                market_address=params.market_address,
                order_id=params.order_id
            )
            
            # Wait for receipt
            receipt = wallet_provider.wait_for_transaction_receipt(tx_hash)
            
            # Check status
            if receipt['status'] == 1:
                return f"Successfully cancelled order {params.order_id} on Kuru. Transaction hash: {tx_hash}"
            else:
                return f"Order cancellation failed. Transaction hash: {tx_hash}"
            
        except Exception as e:
            return f"Failed to cancel order: {str(e)}"
        
    # ... previous code ...
    
    @create_action(
        name="batch-orders",
        description="""
This tool allows submitting multiple orders in a single transaction.
It takes:
- orders: A list of order specifications, each containing:
  - order_type: 'limit' or 'market'
  - side: 'buy' or 'sell'
  - price: Required for limit orders
  - size: Amount to trade
  - min_amount_out: (Optional) For market orders
  - post_only: (Optional) For limit orders
  - cloid: (Optional) Client order ID
- market_address: The address of the market
- network_id: (Optional) Network ID (default: base-mainnet)

Example:
- Submit multiple orders: [{"order_type":"limit","side":"buy","price":"0.00000002","size":"10000"},{"order_type":"limit","side":"sell","price":"0.00000003","size":"10000"}]

Important notes:
- Batch orders are more gas efficient than individual orders
- All orders in a batch must be for the same market
- Supported networks: base-mainnet, base-sepolia
""",
        schema=BatchOrderParams
    )
    async def batch_orders(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> str:
        """Submit multiple orders in a single transaction"""
        params = BatchOrderParams(**args)
        network_id = params.network_id
        
        # Get chain id
        chain_id = NETWORK_ID_TO_CHAIN_ID.get(network_id)
        if not chain_id:
            return f"Unsupported network: {network_id}"
        
        # Initialize Web3
        if not await self._initialize_web3(chain_id):
            return f"Failed to initialize Web3 for network {network_id}"
        
        try:
            # Execute batch orders
            tx_hash = await self._batch_orders(
                wallet_provider=wallet_provider,
                chain_id=chain_id,
                market_address=params.market_address,
                orders=params.orders
            )
            
            # Wait for receipt
            receipt = wallet_provider.wait_for_transaction_receipt(tx_hash)
            
            # Check status
            if receipt['status'] == 1:
                return f"Successfully submitted batch of {len(params.orders)} orders. Transaction hash: {tx_hash}"
            else:
                return f"Batch order transaction failed. Transaction hash: {tx_hash}"
            
        except Exception as e:
            return f"Failed to submit batch orders: {str(e)}"
    
    @create_action(
        name="deposit-margin",
        description="""
This tool allows depositing assets to a Kuru margin account.
It takes:
- token_address: The address of the token to deposit
- amount: The amount to deposit in decimal units
- network_id: (Optional) Network ID (default: base-mainnet)

Example:
- Deposit 10 USDC: token_address=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913, amount=10

Important notes:
- Depositing increases your margin account balance for trading
- You must approve the token for transfer first (this happens automatically)
- Supported networks: base-mainnet, base-sepolia
""",
        schema=MarginActionParams
    )
    async def deposit_margin(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> str:
        """Deposit assets to a Kuru margin account"""
        params = MarginActionParams(**args)
        network_id = params.network_id
        
        # Get chain id
        chain_id = NETWORK_ID_TO_CHAIN_ID.get(network_id)
        if not chain_id:
            return f"Unsupported network: {network_id}"
        
        # Initialize Web3
        if not await self._initialize_web3(chain_id):
            return f"Failed to initialize Web3 for network {network_id}"
        
        try:
            # Deposit to margin account
            tx_hash = await self._deposit_to_margin(
                wallet_provider=wallet_provider,
                chain_id=chain_id,
                token_address=params.token_address,
                amount=params.amount
            )
            
            # Wait for receipt
            receipt = wallet_provider.wait_for_transaction_receipt(tx_hash)
            
            # Check status
            if receipt['status'] == 1:
                return f"Successfully deposited {params.amount} to margin account. Transaction hash: {tx_hash}"
            else:
                return f"Margin deposit transaction failed. Transaction hash: {tx_hash}"
            
        except Exception as e:
            return f"Failed to deposit to margin account: {str(e)}"
    
    @create_action(
        name="view-margin-balance",
        description="""
This tool allows viewing the balance of a token in your Kuru margin account.
It takes:
- token_address: The address of the token to check
- network_id: (Optional) Network ID (default: base-mainnet)

Example:
- Check USDC balance: token_address=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

Important notes:
- This is a read-only action that does not require gas
- Supported networks: base-mainnet, base-sepolia
""",
        schema=MarginActionParams
    )
    async def view_margin_balance(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> str:
        """View token balance in margin account"""
        params = MarginActionParams(**args)
        network_id = params.network_id
        
        # Get chain id
        chain_id = NETWORK_ID_TO_CHAIN_ID.get(network_id)
        if not chain_id:
            return f"Unsupported network: {network_id}"
        
        # Initialize Web3
        if not await self._initialize_web3(chain_id):
            return f"Failed to initialize Web3 for network {network_id}"
        
        try:
            # Get balance
            balance = await self._get_margin_balance(
                wallet_provider=wallet_provider,
                chain_id=chain_id,
                token_address=params.token_address
            )
            
            # Convert from wei to decimal
            balance_decimal = Web3.from_wei(balance, 'ether')
            
            return f"Margin account balance for token {params.token_address}: {balance_decimal}"
            
        except Exception as e:
            return f"Failed to get margin balance: {str(e)}"
    
    @create_action(
        name="get-orderbook",
        description="""
This tool allows viewing the current orderbook for a market.
It takes:
- market_address: The address of the market
- network_id: (Optional) Network ID (default: base-mainnet)

Example:
- View orderbook: market_address=0x05e6f736b5dedd60693fa806ce353156a1b73cf3

Important notes:
- This is a read-only action that does not require gas
- Returns the current state of bids and asks
- Supported networks: base-mainnet, base-sepolia
""",
        schema=OrderbookParams
    )
    async def get_orderbook(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> str:
        """Get the current orderbook for a market"""
        params = OrderbookParams(**args)
        network_id = params.network_id
        
        # Get chain id
        chain_id = NETWORK_ID_TO_CHAIN_ID.get(network_id)
        if not chain_id:
            return f"Unsupported network: {network_id}"
        
        # Initialize Web3
        if not await self._initialize_web3(chain_id):
            return f"Failed to initialize Web3 for network {network_id}"
        
        try:
            # Get orderbook
            orderbook = await self._get_orderbook(
                wallet_provider=wallet_provider,
                chain_id=chain_id,
                market_address=params.market_address
            )
            
            # Format the output
            bids_output = "\n".join([f"Price: {bid['price']}, Size: {bid['size']}" for bid in orderbook["bids"][:5]])
            asks_output = "\n".join([f"Price: {ask['price']}, Size: {ask['size']}" for ask in orderbook["asks"][:5]])
            
            return f"Orderbook for market {params.market_address}:\n\nTop 5 Bids:\n{bids_output}\n\nTop 5 Asks:\n{asks_output}"
            
        except Exception as e:
            return f"Failed to get orderbook: {str(e)}"
        
# ... end of class ...

def kuru_action_provider(
    rpc_url_by_chain_id: Optional[Dict[int, str]] = None,
    ws_url: Optional[str] = None,
    margin_account_by_chain: Optional[Dict[int, str]] = None,
    kuru_router_addresses: Optional[Dict[int, str]] = None
) -> KuruActionProvider:
    """Create a Kuru action provider
    
    Args:
        rpc_url_by_chain_id: Optional mapping of chain IDs to RPC URLs
        ws_url: Optional WebSocket URL for real-time order updates
        margin_account_by_chain: Optional mapping of chain IDs to margin account addresses
        kuru_router_addresses: Optional mapping of chain IDs to Kuru router addresses
        
    Returns:
        A configured KuruActionProvider instance
    """
    return KuruActionProvider(
        rpc_url_by_chain_id=rpc_url_by_chain_id,
        ws_url=ws_url,
        margin_account_by_chain=margin_account_by_chain,
        kuru_router_addresses=kuru_router_addresses
    )