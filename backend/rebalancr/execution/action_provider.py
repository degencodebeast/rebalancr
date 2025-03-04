from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Awaitable, TypedDict

class ActionParameter(TypedDict):
    name: str
    type: str
    description: str
    required: bool

class Action:
    """Representation of an executable action with metadata"""
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 parameters: List[ActionParameter],
                 executor: Callable[..., Awaitable[Dict[str, Any]]]):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.executor = executor
    
    def get_signature(self) -> str:
        """Generate a function signature string for this action"""
        param_strings = []
        
        for param in self.parameters:
            param_str = f"{param['name']}: {param['type']}"
            if not param.get('required', True):
                param_str += " = None"
            param_strings.append(param_str)
            
        return f"{self.name}({', '.join(param_strings)})"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the action with the given parameters"""
        return await self.executor(**kwargs)

class ActionProvider(ABC):
    """Base class for all action providers"""
    
    @abstractmethod
    def get_actions(self) -> List[Action]:
        """Return all actions provided by this provider"""
        pass

class TradeActionProvider(ActionProvider):
    """Provider for trade-related actions"""
    
    def __init__(self, trade_agent, wallet_provider):
        self.trade_agent = trade_agent
        self.wallet_provider = wallet_provider
    
    def get_actions(self) -> List[Action]:
        return [
            Action(
                name="execute_trade",
                description="Buy or sell a specific amount of cryptocurrency",
                parameters=[
                    {"name": "asset", "type": "string", "description": "Symbol of the asset to trade (e.g., ETH, USDC)", "required": True},
                    {"name": "amount", "type": "number", "description": "Amount to trade", "required": True},
                    {"name": "action", "type": "string", "description": "Either 'buy' or 'sell'", "required": True}
                ],
                executor=self._execute_trade
            ),
            Action(
                name="rebalance_portfolio",
                description="Rebalance your portfolio to align with a target allocation or strategy",
                parameters=[
                    {"name": "strategy", "type": "string", "description": "Strategy profile (e.g., 'conservative', 'balanced', 'aggressive')", "required": False}
                ],
                executor=self._rebalance_portfolio
            )
        ]
    
    async def _execute_trade(self, user_id: str, asset: str, amount: float, action: str) -> Dict[str, Any]:
        # Validate parameters
        if action.lower() not in ["buy", "sell"]:
            return {"success": False, "message": "Action must be 'buy' or 'sell'"}
        
        if amount <= 0:
            return {"success": False, "message": "Amount must be greater than 0"}
        
        # Check if user has wallet
        wallet_address = await self.wallet_provider.get_wallet_address(user_id)
        if not wallet_address:
            return {"success": False, "message": "No wallet found for this user"}
        
        # Execute the trade
        return await self.trade_agent.execute_trade(
            user_id=user_id,
            asset=asset,
            amount=amount,
            action=action.lower()
        )
    
    async def _rebalance_portfolio(self, user_id: str, strategy: str = "balanced") -> Dict[str, Any]:
        # Check if user has wallet
        wallet_address = await self.wallet_provider.get_wallet_address(user_id)
        if not wallet_address:
            return {"success": False, "message": "No wallet found for this user"}
        
        # Execute rebalance
        return await self.trade_agent.rebalance_portfolio(
            user_id=user_id,
            strategy=strategy
        ) 