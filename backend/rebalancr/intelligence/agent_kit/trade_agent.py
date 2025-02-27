import logging
from typing import Dict, List, Any, AsyncGenerator

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    wallet_action_provider,
    erc20_action_provider
)

from .wallet_provider import get_wallet_provider

logger = logging.getLogger(__name__)

class TradeAgent:
    """
    Dedicated agent for executing trades and on-chain transactions
    
    Separates trade execution logic from chat and analysis components
    """
    def __init__(self, db_manager, market_analyzer, wallet_provider=None):
        self.db_manager = db_manager
        self.market_analyzer = market_analyzer
        self.wallet_provider = wallet_provider or get_wallet_provider()
        
        # Initialize AgentKit config for trades
        self.agent_kit = self._initialize_agent_kit()
    
    def _initialize_agent_kit(self):
        """Initialize AgentKit with necessary providers for trading"""
        config = AgentKitConfig(
            wallet_provider=self.wallet_provider,
            action_providers=[
                erc20_action_provider(),  # ERC20 token actions
                wallet_action_provider()  # Wallet operations
            ]
        )
        return AgentKit(config)
    
    async def execute_trade(self, user_id: str, asset: str, amount: float, 
                           action: str) -> Dict[str, Any]:
        """
        Execute a trade for a user
        
        Args:
            user_id: User identifier
            asset: Asset symbol to trade
            amount: Amount to trade
            action: "buy" or "sell"
            
        Returns:
            Result of the trade execution
        """
        # Get user wallet
        wallet_info = await self.db_manager.get_agent_wallet(user_id)
        if not wallet_info:
            return {
                "success": False,
                "message": "No wallet found for user"
            }
        
        # Execute trade
        try:
            # Implementation would use AgentKit to execute the trade
            result = await self._execute_transaction(
                wallet_info["address"],
                asset,
                amount,
                action
            )
            
            return {
                "success": True,
                "transaction_id": result.get("tx_hash"),
                "message": f"Successfully {action}ed {amount} {asset}"
            }
        except Exception as e:
            logger.error(f"Trade execution error: {str(e)}")
            return {
                "success": False,
                "message": f"Error executing trade: {str(e)}"
            }
    
    async def rebalance_portfolio(self, user_id: str, 
                                 target_weights: Dict[str, float]) -> Dict[str, Any]:
        """
        Rebalance a user's portfolio to match target weights
        
        Args:
            user_id: User identifier
            target_weights: Target asset allocation
            
        Returns:
            Results of the rebalancing operation
        """
        # Implementation would calculate trades needed and execute them
        pass
        
    async def _execute_transaction(self, wallet_address: str, asset: str, 
                                  amount: float, action: str) -> Dict[str, Any]:
        """Execute a transaction through AgentKit"""
        # Implementation depends on how you want to interface with AgentKit
        pass 