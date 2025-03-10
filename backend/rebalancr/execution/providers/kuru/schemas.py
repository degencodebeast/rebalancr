"""Schemas for Kuru action provider."""

from decimal import Decimal
from typing import List, Optional, Union

from pydantic import BaseModel, Field, validator

class SwapParams(BaseModel):
    """Parameters for swap action."""
    from_token: str = Field(..., description="Address of token to swap from")
    to_token: str = Field(..., description="Address of token to swap to")
    amount_in: Decimal = Field(..., description="Amount of from_token to swap (in decimal units)")
    min_amount_out: Optional[Decimal] = Field(None, description="Minimum amount of to_token to receive")
    slippage_percentage: Optional[float] = Field(0.5, description="Slippage tolerance in percentage")
    network_id: str = Field("base-mainnet", description="Network ID")
    market_address: str = Field(..., description="Address of the market to trade on")
    
    # Computed property
    @property
    def is_buy(self) -> bool:
        """Determine if this is a buy order."""
        # In most DEXs, if to_token is the base asset (like ETH), it's a buy order
        return self.to_token == "0x0000000000000000000000000000000000000000"
    
    @validator("amount_in")
    def amount_must_be_positive(cls, v):
        """Validate that amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @validator("slippage_percentage")
    def slippage_percentage_must_be_reasonable(cls, v):
        """Validate that slippage percentage is reasonable."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Slippage percentage must be between 0 and 100")
        return v

class LimitOrderParams(BaseModel):
    """Parameters for limit order action."""
    from_token: str = Field(..., description="Address of token to sell")
    to_token: str = Field(..., description="Address of token to buy")
    amount_in: Decimal = Field(..., description="Amount of from_token to sell (in decimal units)")
    price: Decimal = Field(..., description="Limit price in to_token per from_token")
    post_only: bool = Field(False, description="Whether to make the order post-only")
    network_id: str = Field("base-mainnet", description="Network ID")
    market_address: str = Field(..., description="Address of the market to trade on")
    
    # Computed property
    @property
    def is_buy(self) -> bool:
        """Determine if this is a buy order."""
        # In most DEXs, if to_token is the base asset (like ETH), it's a buy order
        return self.to_token == "0x0000000000000000000000000000000000000000"
    
    @validator("amount_in", "price")
    def values_must_be_positive(cls, v):
        """Validate that values are positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

class OrderStatusParams(BaseModel):
    """Parameters for order status actions."""
    order_id: str = Field(..., description="Client order ID (cloid)")
    market_address: str = Field(..., description="Address of the market")
    network_id: str = Field("base-mainnet", description="Network ID")

class OrderSpec(BaseModel):
    """Specification for a single order in a batch."""
    order_type: str = Field(..., description="Order type: 'limit' or 'market'")
    side: str = Field(..., description="Order side: 'buy' or 'sell'")
    price: Optional[Decimal] = Field(None, description="Limit price (required for limit orders)")
    size: Decimal = Field(..., description="Order size")
    min_amount_out: Optional[Decimal] = Field(None, description="Minimum amount out (for market orders)")
    post_only: bool = Field(False, description="Whether the order is post-only")
    cloid: Optional[str] = Field(None, description="Client order ID")
    
    @validator("order_type")
    def validate_order_type(cls, v):
        """Validate order type."""
        if v.lower() not in ["limit", "market"]:
            raise ValueError("Order type must be 'limit' or 'market'")
        return v.lower()
    
    @validator("side")
    def validate_side(cls, v):
        """Validate order side."""
        if v.lower() not in ["buy", "sell"]:
            raise ValueError("Side must be 'buy' or 'sell'")
        return v.lower()
    
    @validator("price")
    def validate_price(cls, v, values):
        """Validate price based on order type."""
        if values.get("order_type") == "limit" and (v is None or v <= 0):
            raise ValueError("Price is required for limit orders and must be positive")
        return v

class BatchOrderParams(BaseModel):
    """Parameters for batch orders action."""
    orders: List[OrderSpec] = Field(..., description="List of order specifications")
    market_address: str = Field(..., description="Address of the market")
    network_id: str = Field("base-mainnet", description="Network ID")

class MarginActionParams(BaseModel):
    """Parameters for margin account actions."""
    token_address: str = Field(..., description="Address of the token")
    amount: Optional[Decimal] = Field(None, description="Amount for deposit/withdraw")
    network_id: str = Field("base-mainnet", description="Network ID")
    
    @validator("amount")
    def amount_must_be_positive(cls, v):
        """Validate that amount is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("Amount must be positive")
        return v

class OrderbookParams(BaseModel):
    """Parameters for orderbook query."""
    market_address: str = Field(..., description="Address of the market")
    network_id: str = Field("base-mainnet", description="Network ID")





# from pydantic import BaseModel, Field, validator
# from typing import Optional, List
# from decimal import Decimal

# class TokenAmount(BaseModel):
#     """Token amount with address and amount"""
#     token_address: str = Field(..., description="Token contract address")
#     amount: Decimal = Field(..., description="Token amount in decimal")
    
#     @validator('amount')
#     def amount_must_be_positive(cls, v):
#         if v <= 0:
#             raise ValueError("Amount must be positive")
#         return v

# class SwapParams(BaseModel):
#     """Parameters for swapping tokens on Kuru"""
#     from_token: str = Field(..., description="Address of token to swap from")
#     to_token: str = Field(..., description="Address of token to swap to")
#     amount_in: Decimal = Field(..., description="Amount of from_token to swap")
#     min_amount_out: Optional[Decimal] = Field(None, description="Minimum amount of to_token to receive")
#     slippage_percentage: Optional[float] = Field(0.5, description="Slippage tolerance in percentage")
#     network_id: Optional[str] = Field("base-mainnet", description="Network ID")
#     market_address: str = Field(..., description="Address of the market to trade on")
#     is_buy: bool = Field(True, description="True for buy, False for sell")
    
#     @validator('amount_in')
#     def amount_in_must_be_positive(cls, v):
#         if v <= 0:
#             raise ValueError("Amount in must be positive")
#         return v
    
#     @validator('slippage_percentage')
#     def slippage_must_be_reasonable(cls, v):
#         if v < 0 or v > 100:
#             raise ValueError("Slippage percentage must be between 0 and 100")
#         return v

# class LimitOrderParams(BaseModel):
#     """Parameters for placing a limit order on Kuru"""
#     from_token: str = Field(..., description="Address of token to sell")
#     to_token: str = Field(..., description="Address of token to buy")
#     amount_in: Decimal = Field(..., description="Amount of from_token to sell")
#     price: Decimal = Field(..., description="Limit price in to_token per from_token")
#     post_only: Optional[bool] = Field(False, description="Make order post-only")
#     network_id: Optional[str] = Field("base-mainnet", description="Network ID")
#     market_address: str = Field(..., description="Address of the market to trade on")
#     is_buy: bool = Field(True, description="True for buy, False for sell")
    
#     @validator('amount_in', 'price')
#     def values_must_be_positive(cls, v):
#         if v <= 0:
#             raise ValueError("Values must be positive")
#         return v

# class OrderStatusParams(BaseModel):
#     """Parameters for checking or cancelling an order"""
#     order_id: str = Field(..., description="Client order ID to check or cancel")
#     network_id: Optional[str] = Field("base-mainnet", description="Network ID")

# class OrderSpec(BaseModel):
#     """Specification for a single order within a batch"""
#     order_type: str = Field(..., description="Order type ('limit' or 'market')")
#     side: str = Field(..., description="Order side ('buy' or 'sell')")
#     price: Optional[Decimal] = Field(None, description="Price for limit orders")
#     size: Decimal = Field(..., description="Size of the order")
#     min_amount_out: Optional[Decimal] = Field(None, description="Minimum amount out for market orders")
#     post_only: Optional[bool] = Field(False, description="Make limit order post-only")
#     cloid: Optional[str] = Field(None, description="Client order ID")
    
#     @validator('order_type')
#     def validate_order_type(cls, v):
#         if v not in ["limit", "market"]:
#             raise ValueError("Order type must be 'limit' or 'market'")
#         return v
    
#     @validator('side')
#     def validate_side(cls, v):
#         if v not in ["buy", "sell"]:
#             raise ValueError("Side must be 'buy' or 'sell'")
#         return v
    
#     @validator('price')
#     def validate_price(cls, v, values):
#         if values.get('order_type') == 'limit' and not v:
#             raise ValueError("Price is required for limit orders")
#         return v

# class BatchOrderParams(BaseModel):
#     """Parameters for batch order submission"""
#     market_address: str = Field(..., description="Address of the market")
#     orders: List[OrderSpec] = Field(..., description="List of order specifications")
#     network_id: Optional[str] = Field("base-mainnet", description="Network ID")

# class MarginActionParams(BaseModel):
#     """Parameters for margin account actions"""
#     token_address: str = Field(..., description="Address of token")
#     amount: Optional[Decimal] = Field(None, description="Amount in decimal units (required for deposit)")
#     network_id: Optional[str] = Field("base-mainnet", description="Network ID")
    
#     @validator('amount')
#     def amount_must_be_positive(cls, v, values):
#         if v is not None and v <= 0:
#             raise ValueError("Amount must be positive")
#         return v

# class OrderbookParams(BaseModel):
#     """Parameters for getting orderbook"""
#     market_address: str = Field(..., description="Address of the market")
#     network_id: Optional[str] = Field("base-mainnet", description="Network ID")