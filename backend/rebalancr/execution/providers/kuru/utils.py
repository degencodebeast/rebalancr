from typing import Optional, Dict, Any
from decimal import Decimal

from .constants import TOKEN_ADDRESSES

def get_token_address(chain_id: int, symbol: str) -> Optional[str]:
    """Get the token address for a given symbol and chain ID"""
    chain_tokens = TOKEN_ADDRESSES.get(chain_id, {})
    return chain_tokens.get(symbol.upper())

def format_token_amount(amount: Decimal, decimals: int = 18) -> str:
    """Format a token amount with the correct number of decimals"""
    return str(int(amount * Decimal(10) ** decimals))