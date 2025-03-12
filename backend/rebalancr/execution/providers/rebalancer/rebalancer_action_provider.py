"""
RebalancerActionProvider

Provides actions for portfolio rebalancing, implementing the AgentKit action provider pattern.
"""
import asyncio
from datetime import datetime
import json
import logging
from typing import Dict, List, Any, Optional, Type, Union, cast, TYPE_CHECKING
from pydantic import BaseModel, Field, root_validator, validator
from decimal import Decimal

from coinbase_agentkit.action_providers.action_decorator import create_action
from coinbase_agentkit.action_providers.action_provider import ActionProvider
from coinbase_agentkit.network import Network
from coinbase_agentkit.wallet_providers import EvmWalletProvider

# Use TYPE_CHECKING for circular import prevention
if TYPE_CHECKING:
    from rebalancr.intelligence.intelligence_engine import IntelligenceEngine
else:
    # For runtime, just use Any
    IntelligenceEngine = Any

from rebalancr.intelligence.reviewer import TradeReviewer
from rebalancr.strategy.engine import StrategyEngine
from rebalancr.performance.analyzer import PerformanceAnalyzer
from rebalancr.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

# Supported networks for the rebalancer
SUPPORTED_NETWORKS = [1, 56, 137, 42161, 10]  # Ethereum, BSC, Polygon, Arbitrum, Optimism

class AnalyzePortfolioParams(BaseModel):
    """Parameters for portfolio analysis"""
    portfolio_id: int
    user_id: str = "current_user"
    include_sentiment: bool = True
    include_manipulation_check: bool = True
    
class ExecuteRebalanceParams(BaseModel):
    """Parameters for executing a portfolio rebalance"""
    portfolio_id: int
    user_id: str = "current_user"
    dry_run: bool = False  # If True, analyze but don't execute
    max_slippage_percent: float = Field(ge=0.1, le=5.0, default=1.0)
    
    @validator('max_slippage_percent')
    def validate_slippage(cls, v):
        if v < 0.1 or v > 5.0:
            raise ValueError('Slippage must be between 0.1% and 5.0%')
        return v
        
class SimulateRebalanceParams(BaseModel):
    """Parameters for simulating a portfolio rebalance"""
    portfolio_id: int
    user_id: str = "current_user"
    target_allocations: Dict[str, float] = Field(default_factory=dict)
    
    @root_validator(skip_on_failure=True)
    def validate_allocations(cls, values):
        allocations = values.get('target_allocations', {})
        if not allocations:
            raise ValueError('Target allocations must be provided')
            
        total = sum(allocations.values())
        if abs(total - 1.0) > 0.01:  # Allow small rounding errors
            raise ValueError(f'Target allocations must sum to 1.0 (got {total})')
            
        return values

class GetPerformanceParams(BaseModel):
    """Parameters for getting performance metrics"""
    portfolio_id: Optional[int] = None
    days: int = Field(ge=1, le=365, default=30)
    include_recommendations: bool = True
    
    @validator('days')
    def validate_days(cls, v):
        if v < 1 or v > 365:
            raise ValueError('Days must be between 1 and 365')
        return v

class EnableAutoRebalanceParams(BaseModel):
    """Parameters for enabling automatic rebalancing"""
    portfolio_name: str = "main"
    frequency: str = "daily"  # hourly, daily, weekly, monthly
    max_slippage: float = Field(ge=0.1, le=5.0, default=1.0)
    
    @validator('max_slippage')
    def validate_slippage(cls, v):
        if v < 0.1 or v > 5.0:
            raise ValueError('Slippage must be between 0.1% and 5.0%')
        return v
        
class DisableAutoRebalanceParams(BaseModel):
    """Parameters for disabling automatic rebalancing"""
    portfolio_name: str = "main"
    
class GetRebalancingStatusParams(BaseModel):
    """Parameters for getting rebalancing status"""
    portfolio_name: str = "main"

class RebalancerActionProvider(ActionProvider):
    """
    Action provider for portfolio rebalancing
    
    Implements Rose Heart's dual-system approach:
    - AI for sentiment analysis (via Intelligence Engine)
    - Statistical methods for numerical operations (via Strategy Engine)
    - Additional validation layer (Trade Reviewer)
    """
    
    def __init__(
        self,
        wallet_provider: EvmWalletProvider,
        intelligence_engine: IntelligenceEngine,
        strategy_engine: StrategyEngine,
        trade_reviewer: TradeReviewer,
        performance_analyzer: PerformanceAnalyzer,
        db_manager: DatabaseManager,
        context: Dict[str, Any] = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(
            name="rebalancer-action",
            action_providers=[]
        )
        self.wallet_provider = wallet_provider
        self.intelligence_engine = intelligence_engine
        self.strategy_engine = strategy_engine
        self.trade_reviewer = trade_reviewer
        self.performance_analyzer = performance_analyzer
        self.db_manager = db_manager
        self.context = context or {}
        self.config = config or {}
        
    def supports_network(self, network_id: int) -> bool:
        """Check if the network is supported by this provider"""
        return network_id in SUPPORTED_NETWORKS
    
    @create_action(
        name="analyze-portfolio",
        description="Analyze a portfolio and provide rebalancing recommendations",
        schema=AnalyzePortfolioParams
    )
    async def analyze_portfolio(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a portfolio and provide recommendations
        
        This uses the intelligence engine which combines:
        - Allora sentiment analysis (emotional signals)
        - Statistical methods (numerical signals)
        """
        params = AnalyzePortfolioParams(**args)
        
        try:
            intelligence_results = await self.intelligence_engine.analyze_portfolio(
                params.user_id, 
                params.portfolio_id
            )
            
            # Additional strategy-specific analysis
            strategy_results = await self.strategy_engine.analyze_portfolio(
                intelligence_results.get("assets", [])
            )
            
            # Get market conditions
            market_condition = strategy_results.get("market_condition", "normal")
            
            # Validate using the reviewer
            validation = None
            if params.include_sentiment and len(intelligence_results.get("assets", [])) > 0:
                validation = await self.trade_reviewer.validate_rebalance_plan(
                    intelligence_results.get("assets", []),
                    market_condition
                )
            
            result = {
                "portfolio_id": params.portfolio_id,
                "rebalance_needed": intelligence_results.get("rebalance_needed", False),
                "assets": intelligence_results.get("assets", []),
                "cost_analysis": intelligence_results.get("cost_analysis", {}),
                "strategy_analysis": {
                    "market_condition": market_condition,
                    "risk_level": strategy_results.get("risk_level", "medium"),
                    "recommendations": strategy_results.get("recommendations", [])
                }
            }
            
            if validation:
                result["validation"] = {
                    "approved": validation.get("approved", False),
                    "approval_rate": validation.get("approval_rate", 0),
                    "overall_risk": validation.get("overall_risk", 5)
                }
                
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            return {
                "portfolio_id": params.portfolio_id,
                "error": str(e)
            }
    
    @create_action(
        name="execute-rebalance",
        description="Execute a portfolio rebalance based on AI and statistical analysis",
        schema=ExecuteRebalanceParams
    )
    async def execute_rebalance(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a portfolio rebalance
        
        This implements Rose Heart's approach by:
        1. Getting recommendations from intelligence engine (AI + statistical)
        2. Validating with reviewer (3rd component)
        3. Only executing if all components agree
        4. Being cautious about fees (cost-benefit analysis)
        """
        params = ExecuteRebalanceParams(**args)
        
        try:
            # First, analyze the portfolio to get recommendations
            analysis_result = await self.analyze_portfolio(wallet_provider, {
                "portfolio_id": params.portfolio_id,
                "user_id": params.user_id,
                "include_sentiment": True,
                "include_manipulation_check": True
            })
            
            # Check if rebalancing is needed
            if not analysis_result.get("rebalance_needed", False):
                return {
                    "portfolio_id": params.portfolio_id,
                    "executed": False,
                    "reason": "Rebalancing not needed",
                    "analysis": analysis_result
                }
                
            # Check validation if available
            validation = analysis_result.get("validation", {})
            if not validation.get("approved", False) and validation:
                return {
                    "portfolio_id": params.portfolio_id,
                    "executed": False,
                    "reason": "Rebalancing not approved by validator",
                    "approval_rate": validation.get("approval_rate", 0),
                    "analysis": analysis_result
                }
                
            # Check if dry run - if so, return the analysis without executing
            if params.dry_run:
                return {
                    "portfolio_id": params.portfolio_id,
                    "executed": False,
                    "reason": "Dry run requested",
                    "analysis": analysis_result
                }
                
            # Execute the rebalance trades
            trades = analysis_result.get("cost_analysis", {}).get("trades", [])
            execution_results = []
            
            for trade in trades:
                symbol = trade.get("symbol")
                amount = trade.get("amount")
                value = trade.get("value")
                
                if amount > 0:
                    # Buy operation
                    execution_result = await self._execute_buy(
                        params.user_id,
                        symbol,
                        abs(amount),
                        params.max_slippage_percent
                    )
                elif amount < 0:
                    # Sell operation
                    execution_result = await self._execute_sell(
                        params.user_id,
                        symbol,
                        abs(amount),
                        params.max_slippage_percent
                    )
                else:
                    # Skip zero amount trades
                    continue
                    
                execution_results.append({
                    "symbol": symbol,
                    "amount": amount,
                    "value": value,
                    "success": execution_result.get("success", False),
                    "tx_hash": execution_result.get("tx_hash"),
                    "error": execution_result.get("error")
                })
                
            # Log the rebalance for performance tracking
            if execution_results:
                await self.performance_analyzer.log_rebalance({
                    "portfolio_id": params.portfolio_id,
                    "assets": analysis_result.get("assets", []),
                    "market_condition": analysis_result.get("strategy_analysis", {}).get("market_condition", "normal"),
                    "timestamp": analysis_result.get("timestamp")
                })
                
            # Return the results
            all_succeeded = all(result.get("success", False) for result in execution_results)
            return {
                "portfolio_id": params.portfolio_id,
                "executed": True,
                "success": all_succeeded,
                "trades": execution_results,
                "analysis": analysis_result
            }
            
        except Exception as e:
            logger.error(f"Error executing rebalance: {str(e)}")
            return {
                "portfolio_id": params.portfolio_id,
                "executed": False,
                "error": str(e)
            }
    
    @create_action(
        name="simulate-rebalance",
        description="Simulate a portfolio rebalance with custom allocations",
        schema=SimulateRebalanceParams
    )
    async def simulate_rebalance(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate a portfolio rebalance with custom allocations
        
        This is useful for testing different allocation strategies before executing
        """
        params = SimulateRebalanceParams(**args)
        
        try:
            # Get current portfolio
            portfolio = await self.intelligence_engine.get_portfolio(
                params.user_id,
                params.portfolio_id
            )
            
            # Calculate trades needed for the target allocations
            current_values = {
                asset["symbol"]: asset["value"]
                for asset in portfolio.get("assets", [])
            }
            current_weights = {
                asset["symbol"]: asset["weight"]
                for asset in portfolio.get("assets", [])
            }
            
            # Calculate total portfolio value
            total_value = sum(current_values.values())
            
            # Calculate trades
            trades = []
            for symbol, target_weight in params.target_allocations.items():
                current_weight = current_weights.get(symbol, 0)
                current_value = current_values.get(symbol, 0)
                
                target_value = total_value * target_weight
                value_change = target_value - current_value
                
                # Get current price
                current_price = None
                for asset in portfolio.get("assets", []):
                    if asset["symbol"] == symbol:
                        current_price = asset.get("price", 0)
                        break
                        
                if not current_price or current_price <= 0:
                    # Skip assets with no price data
                    continue
                    
                amount_change = value_change / current_price
                
                trades.append({
                    "symbol": symbol,
                    "amount": amount_change,
                    "value": value_change,
                    "price": current_price,
                    "weight_change": target_weight - current_weight
                })
                
            # Calculate estimated costs (fees)
            fee_rate = self.config.get("FEE_RATE", 0.001)  # Default 0.1%
            estimated_fees = sum(abs(t["value"]) * fee_rate for t in trades)
            
            # Get current market condition
            market_condition = await self.strategy_engine.get_market_condition()
            
            # Get validation from reviewer
            validation = await self.trade_reviewer.validate_rebalance_plan(
                [{"asset": t["symbol"], "action": "increase" if t["amount"] > 0 else "decrease"}
                for t in trades if t["amount"] != 0],
                market_condition
            )
            
            return {
                "portfolio_id": params.portfolio_id,
                "total_value": total_value,
                "current_weights": current_weights,
                "target_weights": params.target_allocations,
                "trades": trades,
                "estimated_fees": estimated_fees,
                "market_condition": market_condition,
                "validation": validation
            }
            
        except Exception as e:
            logger.error(f"Error simulating rebalance: {str(e)}")
            return {
                "portfolio_id": params.portfolio_id,
                "error": str(e)
            }
    
    @create_action(
        name="get-performance",
        description="Get performance metrics and recommendations for a portfolio",
        schema=GetPerformanceParams
    )
    async def get_performance(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance metrics and recommendations"""
        params = GetPerformanceParams(**args)
        
        try:
            # Get performance data
            performance = await self.performance_analyzer.analyze_performance(
                params.portfolio_id
            )
            
            # If recommendations requested, generate report
            if params.include_recommendations:
                report = await self.performance_analyzer.generate_performance_report(
                    params.days
                )
                performance["report"] = report
                
            return performance
            
        except Exception as e:
            logger.error(f"Error getting performance: {str(e)}")
            return {
                "error": str(e)
            }
    
    @create_action(
        name="enable-auto-rebalance-from-text",
        description="Enable automatic portfolio rebalancing from natural language request",
        schema=EnableAutoRebalanceParams
    )
    async def enable_auto_rebalance_from_text(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> Dict[str, Any]:
        """Enable automatic rebalancing based on natural language request"""
        params = EnableAutoRebalanceParams(**args)
        user_id = self.context.get("user_id", "current_user")
        
        logger.info(f"Enabling auto-rebalance for user {user_id}, portfolio {params.portfolio_name}")
        
        # Convert frequency to check interval
        interval_mapping = {
            "hourly": 3600,
            "daily": 86400,
            "weekly": 604800,
            "monthly": 2592000
        }
        check_interval = interval_mapping.get(params.frequency.lower(), 86400)  # Default to daily
        
        # Resolve portfolio name to ID
        portfolio_id = await self._resolve_portfolio_name(user_id, params.portfolio_name)
        if not portfolio_id:
            return {
                "status": "error",
                "message": f"Could not find portfolio named '{params.portfolio_name}'"
            }
        
        # Update portfolio settings - use 1 for true in SQLite
        updated = await self.db_manager.update_portfolio(
            portfolio_id,
            {
                "auto_rebalance": 1,  # SQLite boolean as integer
                "max_slippage": params.max_slippage,
                "check_interval": check_interval
            }
        )
        
        if updated:
            # Get human-readable frequency
            human_frequency = params.frequency.lower()
            return {
                "status": "success",
                "message": f"Automatic rebalancing enabled for your {params.portfolio_name} portfolio. " +
                        f"It will be checked {human_frequency} with max slippage of {params.max_slippage}%."
            }
        else:
            return {
                "status": "error",
                "message": f"Could not enable automatic rebalancing for {params.portfolio_name} portfolio."
            }

    @create_action(
        name="disable-auto-rebalance-from-text",
        description="Disable automatic portfolio rebalancing from natural language request",
        schema=DisableAutoRebalanceParams
    )
    async def disable_auto_rebalance_from_text(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> Dict[str, Any]:
        """Disable automatic rebalancing based on natural language request"""
        params = DisableAutoRebalanceParams(**args)
        user_id = self.context.get("user_id", "current_user")
        
        logger.info(f"Disabling auto-rebalance for user {user_id}, portfolio {params.portfolio_name}")
        
        # Resolve portfolio name to ID
        portfolio_id = await self._resolve_portfolio_name(user_id, params.portfolio_name)
        if not portfolio_id:
            return {
                "status": "error",
                "message": f"Could not find portfolio named '{params.portfolio_name}'"
            }
        
        # Update portfolio settings - use 0 for false in SQLite
        updated = await self.db_manager.update_portfolio(
            portfolio_id,
            {
                "auto_rebalance": 0  # SQLite boolean as integer
            }
        )
        
        if updated:
            return {
                "status": "success",
                "message": f"Automatic rebalancing disabled for your {params.portfolio_name} portfolio."
            }
        else:
            return {
                "status": "error",
                "message": f"Could not disable automatic rebalancing for {params.portfolio_name} portfolio."
            }

    @create_action(
        name="get-rebalancing-status",
        description="Get the current status of the rebalancing strategy",
        schema=GetRebalancingStatusParams
    )
    async def get_rebalancing_status(self, wallet_provider: EvmWalletProvider, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current rebalancing status for a portfolio"""
        params = GetRebalancingStatusParams(**args)
        user_id = self.context.get("user_id", "current_user")
        
        # Resolve portfolio name to ID
        portfolio_id = await self._resolve_portfolio_name(user_id, params.portfolio_name)
        if not portfolio_id:
            return {
                "status": "error",
                "message": f"Could not find portfolio named '{params.portfolio_name}'"
            }
        
        # Get portfolio details
        portfolio = await self._get_portfolio_by_id(portfolio_id)
        if not portfolio:
            return {
                "status": "error",
                "message": f"Could not retrieve details for portfolio {params.portfolio_name}"
            }
        
        # Check auto-rebalance status
        is_active = portfolio.get("auto_rebalance", 0) == 1
        check_interval = portfolio.get("check_interval", 86400)
        max_slippage = portfolio.get("max_slippage", 1.0)
        
        # Convert check interval to human-readable format
        frequency = "daily"
        if check_interval <= 3600:
            frequency = "hourly"
        elif check_interval <= 86400:
            frequency = "daily"
        elif check_interval <= 604800:
            frequency = "weekly"
        else:
            frequency = "monthly"
        
        if is_active:
            return {
                "status": "active",
                "message": f"Automatic rebalancing is active for your {params.portfolio_name} portfolio. " +
                          f"It is checked {frequency} with maximum slippage of {max_slippage}%."
            }
        else:
            return {
                "status": "inactive",
                "message": f"Automatic rebalancing is not active for your {params.portfolio_name} portfolio."
            }
    
    async def _execute_buy(self, user_id: str, symbol: str, amount: float, max_slippage_percent: float) -> Dict[str, Any]:
        """Execute a buy operation"""
        # In a real implementation, this would connect to exchange APIs
        # For the hackathon, simulate a successful transaction
        await asyncio.sleep(0.5)  # Simulate API call
        
        return {
            "success": True,
            "tx_hash": f"0x{hash(f'{user_id}_{symbol}_{amount}_{datetime.now().timestamp()}'):#x}",
            "asset": symbol,
            "amount": amount,
            "side": "buy"
        }
    
    async def _execute_sell(self, user_id: str, symbol: str, amount: float, max_slippage_percent: float) -> Dict[str, Any]:
        """Execute a sell operation"""
        # In a real implementation, this would connect to exchange APIs
        # For the hackathon, simulate a successful transaction
        await asyncio.sleep(0.5)  # Simulate API call
        
        return {
            "success": True,
            "tx_hash": f"0x{hash(f'{user_id}_{symbol}_{amount}_{datetime.now().timestamp()}'):#x}",
            "asset": symbol,
            "amount": amount,
            "side": "sell"
        }
        
    async def _resolve_portfolio_name(self, user_id: str, portfolio_name: str) -> Optional[int]:
        """Helper function to convert portfolio name to ID"""
        # Get user's portfolios
        portfolios = await self._get_user_portfolios(user_id)
        
        # Look for exact name match
        for portfolio in portfolios:
            if portfolio.get("name", "").lower() == portfolio_name.lower():
                return portfolio.get("id")
        
        # If not found and portfolio_name is "main" or "default", return first portfolio
        if portfolio_name.lower() in ["main", "default"] and portfolios:
            return portfolios[0].get("id")
        
        # No matching portfolio found
        return None
    
    async def _get_user_portfolios(self, user_id: str) -> List[Dict[str, Any]]:
        """Get portfolios for a user"""
        # This should be implemented based on how you retrieve user portfolios
        # Using your existing db_manager implementation
        return await self.db_manager.get_user_portfolios(user_id)
    
    async def _get_portfolio_by_id(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Get portfolio by ID"""
        # This should be implemented based on how you retrieve portfolios
        # Using your existing db_manager implementation
        return await self.db_manager.get_portfolio(portfolio_id)

def rebalancer_action_provider(
    wallet_provider: EvmWalletProvider,
    intelligence_engine: IntelligenceEngine,
    strategy_engine: StrategyEngine,
    trade_reviewer: TradeReviewer,
    performance_analyzer: PerformanceAnalyzer,
    db_manager: DatabaseManager,  # Added this parameter
    context: Dict[str, Any] = None,  # Added this parameter
    config: Dict[str, Any] = None
) -> RebalancerActionProvider:
    """Create a Rebalancer action provider instance"""
    return RebalancerActionProvider(
        wallet_provider=wallet_provider,
        intelligence_engine=intelligence_engine,
        strategy_engine=strategy_engine,
        trade_reviewer=trade_reviewer,
        performance_analyzer=performance_analyzer,
        db_manager=db_manager,  # Pass db_manager
        context=context,  # Pass context
        config=config
    ) 