"""Utility functions for Kuru action provider."""

from typing import Any, Dict, Optional, Union
from decimal import Decimal

from fastapi import logger
from web3 import Web3
from web3.types import Wei

from coinbase_agentkit.wallet_providers import EvmWalletProvider
from .constants import ERC20_ABI, TOKEN_ADDRESSES

def get_token_address(token_symbol: str, chain_id: int) -> str:
    """Get token address from symbol"""
    if token_symbol.upper() == "ETH":
        return "0x0000000000000000000000000000000000000000"
    
    token_address = TOKEN_ADDRESSES.get(token_symbol.upper(), {}).get(chain_id)
    if not token_address:
        raise ValueError(f"Unknown token symbol {token_symbol} for chain {chain_id}")
    
    return token_address

def format_token_amount(amount: Union[str, int, float, Decimal], decimals: int = 18) -> int:
    """Format token amount to wei"""
    if isinstance(amount, str):
        amount = Decimal(amount)
    
    if isinstance(amount, (int, float)):
        amount = Decimal(str(amount))
    
    # Convert to wei
    return int(amount * Decimal(10) ** Decimal(decimals))

def get_token_decimals(wallet_provider: EvmWalletProvider, token_address: str) -> int:
    """Get token decimals"""
    # ETH has 18 decimals
    if token_address == "0x0000000000000000000000000000000000000000":
        return 18
    
    # For ERC20 tokens, get decimals from contract
    try:
        # Create contract instance
        contract = wallet_provider._web3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        # Call decimals function
        return contract.functions.decimals().call()
    except Exception as e:
        # Default to 18 decimals if something goes wrong
        return 18

def get_token_balance(wallet_provider: EvmWalletProvider, token_address: str) -> int:
    """Get token balance for address"""
    address = wallet_provider.get_address()
    
    # For ETH, get balance from web3
    if token_address == "0x0000000000000000000000000000000000000000":
        return wallet_provider._web3.eth.get_balance(address)
    
    # For ERC20 tokens, call balanceOf
    try:
        # Create contract instance
        contract = wallet_provider._web3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        # Call balanceOf function
        return contract.functions.balanceOf(address).call()
    except Exception as e:
        return 0

def approve_token(wallet_provider: EvmWalletProvider, token_address: str, spender_address: str, amount: int) -> Dict[str, Any]:
    """Approve a spender to use tokens
    
    Args:
        wallet_provider: The wallet provider
        token_address: The address of the token to approve
        spender_address: The address of the spender to approve
        amount: The amount to approve in wei
        
    Returns:
        Transaction receipt
        
    Raises:
        Exception: If the approval transaction fails
    """
    # Native ETH doesn't need approval
    if token_address == "0x0000000000000000000000000000000000000000":
        return None
        
    try:
        # Create token contract
        contract = Web3().eth.contract(address=token_address, abi=ERC20_ABI)
        
        # Encode the approve function call
        encoded_data = contract.encodeABI(
            fn_name="approve",
            args=[spender_address, amount]
        )
        
        # Prepare transaction
        tx_params = {
            "to": token_address,
            "data": encoded_data,
        }
        
        # Send transaction
        tx_hash = wallet_provider.send_transaction(tx_params)
        
        # Wait for receipt and return it
        receipt = wallet_provider.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] != 1:
            raise Exception(f"Approval transaction failed with hash: {tx_hash}")
            
        return receipt
    except Exception as e:
        raise Exception(f"Error approving token: {str(e)}")

def estimate_gas_with_buffer(
    tx_params: Dict[str, Any],
    buffer_percentage: float = 20.0
) -> int:
    """Estimate gas with buffer"""
    try:
        gas_estimate = Web3().eth.estimate_gas(tx_params)
        # Add buffer for safety
        return int(gas_estimate * (1 + buffer_percentage / 100))
    except Exception as e:
        # Fallback to default gas limit
        logger.warning(f"Error estimating gas: {str(e)}")
        return 500000  # Default gas limit





# from typing import Optional, Dict, Any
# from decimal import Decimal
# import asyncio
# from web3 import Web3

# from .constants import TOKEN_ADDRESSES

# def get_token_address(chain_id: int, symbol: str) -> Optional[str]:
#     """Get the token address for a given symbol and chain ID"""
#     chain_tokens = TOKEN_ADDRESSES.get(chain_id, {})
#     return chain_tokens.get(symbol.upper())

# def format_token_amount(amount: Decimal, decimals: int = 18) -> str:
#     """Format a token amount with the correct number of decimals"""
#     return str(int(amount * Decimal(10) ** decimals))

# async def approve_token(client, wallet_provider, token_address: str, spender_address: str, amount: float) -> str:
#     """Approve spender to use tokens
    
#     Args:
#         client: KuruClient instance
#         wallet_provider: Wallet provider
#         token_address: Address of token to approve
#         spender_address: Address of spender to approve
#         amount: Amount to approve (in decimal units)
    
#     Returns:
#         Transaction hash of the approval transaction
#     """
#     # Convert amount to appropriate units
#     token_info = await client.get_token_info(token_address)
#     decimals = token_info.get('decimals', 18)
#     amount_wei = Web3.to_wei(amount, 'ether' if decimals == 18 else 'mwei' if decimals == 6 else 'ether')
    
#     # Prepare the approval transaction
#     approval_data = client.token_contract.encodeABI(
#         fn_name='approve',
#         args=[spender_address, amount_wei]
#     )
    
#     params = {
#         'to': token_address,
#         'data': approval_data
#     }
    
#     # Send the transaction
#     tx_hash = wallet_provider.send_transaction(params)
    
#     # Wait for the transaction to be mined
#     await client.wait_for_transaction(tx_hash)
    
#     return tx_hash

# async def verify_transaction_success(client, tx_hash: str, max_attempts: int = 5) -> bool:
#     """Verify that a transaction was successful"""
#     for i in range(max_attempts):
#         try:
#             receipt = await client.wait_for_transaction(tx_hash)
#             if receipt and receipt.get('status') == 1:
#                 return True
#             elif receipt:
#                 return False
#         except Exception:
#             if i == max_attempts - 1:
#                 return False
#             # Wait longer between attempts
#             await asyncio.sleep(2 ** i)  # Exponential backoff
#     return False