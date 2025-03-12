"""Schemas for Kuru action provider."""

from decimal import Decimal
from typing import List, Optional, Union

from pydantic import BaseModel, Field, validator

class SwapParams(BaseModel):
    """Parameters for swap action."""
    from_token: str = Field(..., description="Address of token to swap from")
    to_token: str = Field(..., description="Address of token to swap to")
    amount_in: str = Field(..., description="Amount of from_token to swap (in decimal units)")
    min_amount_out: Optional[str] = Field(None, description="Minimum amount of to_token to receive")
    slippage_percentage: Optional[float] = Field(0.5, description="Slippage tolerance in percentage")
    network_id: str = Field("monad-testnet", description="Network ID")
    market_address: str = Field(..., description="Address of the market to trade on")
    
    # Computed property
    @property
    def is_buy(self) -> bool:
        """Determine if this is a buy order."""
        return self.to_token == "0x0000000000000000000000000000000000000000"
    
    @validator("amount_in")
    def validate_amount(cls, v):
        """Validate that amount is positive and a valid number."""
        try:
            amount = Decimal(v)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            return v
        except:
            raise ValueError("Amount must be a valid number")

class OrderSpec(BaseModel):
    """Specification for a single order in a batch."""
    order_type: str = Field(..., description="Order type: 'limit' or 'market'")
    side: str = Field(..., description="Order side: 'buy' or 'sell'")
    price: Optional[str] = Field(None, description="Limit price (required for limit orders)")
    size: str = Field(..., description="Order size")
    min_amount_out: Optional[str] = Field(None, description="Minimum amount out (for market orders)")
    post_only: bool = Field(False, description="Whether the order is post-only")
    cloid: Optional[str] = Field(None, description="Client order ID")

class LimitOrderParams(BaseModel):
    """Parameters for limit order action."""
    from_token: str = Field(..., description="Address of token to sell")
    to_token: str = Field(..., description="Address of token to buy")
    amount_in: str = Field(..., description="Amount of from_token to sell (in decimal units)")
    price: str = Field(..., description="Limit price in to_token per from_token")
    post_only: bool = Field(False, description="Whether to make the order post-only")
    network_id: str = Field("monad-testnet", description="Network ID")
    market_address: str = Field(..., description="Address of the market to trade on")
    
    # Computed property
    @property
    def is_buy(self) -> bool:
        """Determine if this is a buy order."""
        return self.to_token == "0x0000000000000000000000000000000000000000"

class OrderStatusParams(BaseModel):
    """Parameters for order status actions."""
    order_id: str = Field(..., description="Client order ID (cloid)")
    market_address: str = Field(..., description="Address of the market")
    network_id: str = Field("monad-testnet", description="Network ID")

class BatchOrderParams(BaseModel):
    """Parameters for batch orders action."""
    orders: List[OrderSpec] = Field(..., description="List of order specifications")
    market_address: str = Field(..., description="Address of the market")
    network_id: str = Field("monad-testnet", description="Network ID")

class MarginActionParams(BaseModel):
    """Parameters for margin account actions."""
    token_address: str = Field(..., description="Address of the token")
    amount: Optional[str] = Field(None, description="Amount for deposit/withdraw")
    network_id: str = Field("monad-testnet", description="Network ID")

class OrderbookParams(BaseModel):
    """Parameters for orderbook query."""
    market_address: str = Field(..., description="Address of the market")
    network_id: str = Field("monad-testnet", description="Network ID")