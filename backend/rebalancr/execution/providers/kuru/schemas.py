from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal

class TokenAmount(BaseModel):
    """Token amount with address and amount"""
    token_address: str = Field(..., description="Token contract address")
    amount: Decimal = Field(..., description="Token amount in decimal")
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

class SwapParams(BaseModel):
    """Parameters for swapping tokens on Kuru"""
    from_token: str = Field(..., description="Address of token to swap from")
    to_token: str = Field(..., description="Address of token to swap to")
    amount_in: Decimal = Field(..., description="Amount of from_token to swap")
    min_amount_out: Optional[Decimal] = Field(None, description="Minimum amount of to_token to receive")
    slippage_percentage: Optional[float] = Field(0.5, description="Slippage tolerance in percentage")
    chain_id: Optional[int] = Field(8453, description="Chain ID (default: Base)")
    
    @validator('amount_in')
    def amount_in_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount in must be positive")
        return v
    
    @validator('slippage_percentage')
    def slippage_must_be_reasonable(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Slippage percentage must be between 0 and 100")
        return v

class LimitOrderParams(BaseModel):
    """Parameters for placing a limit order on Kuru"""
    from_token: str = Field(..., description="Address of token to sell")
    to_token: str = Field(..., description="Address of token to buy")
    amount_in: Decimal = Field(..., description="Amount of from_token to sell")
    price: Decimal = Field(..., description="Limit price in to_token per from_token")
    expiry: Optional[int] = Field(None, description="Order expiry timestamp")
    chain_id: Optional[int] = Field(8453, description="Chain ID (default: Base)")