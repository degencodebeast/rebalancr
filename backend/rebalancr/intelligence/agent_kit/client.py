from typing import Dict, Any, Optional, TYPE_CHECKING
import asyncio
import aiohttp
import logging
import json

from ...config import Settings
from ...intelligence.agent_kit.agent_manager import AgentManager
from ..allora.client import AlloraClient
from ..market_analysis import MarketAnalyzer
from .service import AgentKitService

# Use conditional import to avoid circular imports
if TYPE_CHECKING:
    from ..intelligence_engine import IntelligenceEngine

logger = logging.getLogger(__name__)

class AgentKitClient:
    """
    Client for business logic and domain-specific operations.
    
    This client focuses on:
    - Domain-specific operations (market predictions, portfolio rebalancing)
    - Integration with external services (Allora, market analysis)
    - High-level business workflows
    
    It does NOT handle:
    - Agent creation and management (handled by AgentManager)
    - WebSocket communication (handled by WebSocketMessageHandler)
    - Low-level infrastructure (handled by AgentKitService)
    """
    def __init__(self, config: Settings, intelligence_engine=None):
        """Initialize the client with references to required services."""
        # Get the service and manager singletons
        self.service = AgentKitService.get_instance(config)
        self.agent_manager = AgentManager.get_instance(config)
        
        # Store conversations by user
        self.conversations = {}
        
        # Initialize domain-specific services
        self.allora_client = AlloraClient(api_key=config.ALLORA_API_KEY)
        self.market_analyzer = MarketAnalyzer()
        
        # Initialize intelligence engine reference
        self.intelligence_engine = intelligence_engine
        
    def set_intelligence_engine(self, intelligence_engine):
        """Set the intelligence engine after initialization"""
        self.intelligence_engine = intelligence_engine
        
    async def initialize_session(self, user_id):
        """Initialize a new conversation for a user"""
        conversation = await self.service.create_conversation(user_id)
        self.conversations[user_id] = conversation.id
        return conversation.id

    #Can be used for rest api connections    
    async def get_agent_response(self, user_id, message, session_id=None):
        """
        Send a message and get a response
        
        This is a high-level method that handles:
        1. Using AgentManager for the core agent interaction
        2. Optionally enriching responses with business context
        """
        # Use the AgentManager to get the basic response
        response = await self.agent_manager.get_agent_response(user_id, message, session_id)
        
        # Here you could enrich the response with business context if needed
        # For example, adding market data or portfolio recommendations
        
        return response
    
    #I can map this function to endpoints incase I want the UI to access these functions
    async def process_chat_action(self, user_id, intent, parameters, session_id=None):
        """
        Process a structured action from API/UI directly.
        
        This is NOT used by the agent's ReAct pattern, but provides
        a direct entry point for UI components and API endpoints.
        """
        # Handle different intents with domain-specific logic
        if intent == "get_market_prediction":
            return await self._handle_market_prediction(user_id, parameters)
        elif intent == "rebalance_portfolio":
            return await self._handle_portfolio_rebalance(user_id, parameters)
        else:
            return {"error": f"Unknown intent: {intent}"}
    
    async def execute_trade(self, user_id, params):
        """
        Execute a trade for a user
        
        Business logic method that:
        1. Validates trade parameters
        2. Checks market conditions
        3. Uses AgentManager to execute the transaction
        """
        logger.info(f"Preparing to execute trade: {params}")
        
        # Here you would add business validation of the trade parameters
        
        # Execute the trade via the AgentManager
        async with self.agent_manager.get_agent_executor(user_id) as agent:
            # Format the trade request
            trade_message = f"Execute trade: Buy {params.get('amount')} of {params.get('asset')}"
            
            # Execute the trade
            result = await agent.ainvoke({"messages": [trade_message]})
            
            # Process the result
            return {
                "success": True,
                "transaction_id": "tx_" + str(hash(str(result))),
                "details": result
            }
    
    # Domain-specific operations
    
    async def _handle_market_prediction(self, user_id, parameters):
        """Handle market prediction through ReAct pattern"""
        try:
            async with self.agent_manager.get_agent_executor(user_id) as agent:
                asset = parameters.get("asset", "BTC")
                
                result = await agent.ainvoke({
                    "messages": [{
                        "role": "user",
                        "content": f"Analyze the market for {asset} and provide a prediction with sentiment analysis."
                    }]
                })
                
                return result
        except Exception as e:
            logger.error(f"Error getting market prediction: {str(e)}")
            return {"error": f"Failed to get prediction: {str(e)}"}
    
    async def _handle_portfolio_rebalance(self, user_id, parameters):
        """Handle portfolio rebalancing through ReAct pattern"""
        try:
            # First ensure wallet is loaded 
            async with self.agent_manager.get_agent_executor(user_id) as agent:
                wallet_info_result = await agent.ainvoke({"messages": ["What is my wallet address?"]})
                wallet_address = self._extract_wallet_address(wallet_info_result)
                
                # Now proceed with rebalance through ReAct pattern
                result = await agent.ainvoke({
                    "messages": [{
                        "role": "user",
                        "content": f"Analyze my portfolio with address {wallet_address} and execute a rebalance with these parameters: {json.dumps(parameters)}"
                    }]
                })
                
                return result
        except Exception as e:
            logger.error(f"Error rebalancing portfolio: {str(e)}")
            return {"error": f"Failed to rebalance portfolio: {str(e)}"}
    
    # Helper methods
    
    def _extract_wallet_address(self, result):
        """Extract wallet address from agent response"""
        # Implement parsing logic based on your response format
        # This is a placeholder
        return "0x123456789abcdef"
    
    async def _execute_trades(self, user_id, trades):
        """Execute a set of trades for portfolio rebalancing"""
        results = []
        for asset, amount in trades.items():
            if amount > 0:  # Buy
                params = {
                    "asset": asset,
                    "amount": abs(amount),
                    "action": "buy"
                }
            else:  # Sell
                params = {
                    "asset": asset,
                    "amount": abs(amount),
                    "action": "sell"
                }
            result = await self.execute_trade(user_id, params)
            results.append(result)
        return results
    
    async def _get_user_portfolio(self, wallet_address):
        """Get user's current portfolio holdings"""
        # Implementation depends on your data sources
        # This is a placeholder
        return {"BTC": 0.1, "ETH": 1.5}
    
    async def _get_current_prices(self, assets):
        """Get current prices for assets"""
        # Implementation depends on your data sources
        # This is a placeholder
        return {"BTC": 60000, "ETH": 3000}
    
    async def _get_historical_data(self, asset):
        """Get historical data for statistical analysis"""
        # Implementation depends on your data sources
        # This is a placeholder
        return [{"price": 60000, "timestamp": "2023-01-01"}]
    
    def _generate_recommendation(self, prediction, metrics):
        """Generate a recommendation combining AI sentiment and statistical metrics"""
        recommendation = "HOLD"
        confidence = 0
        
        # Use AI prediction for sentiment-based signals
        sentiment_score = 0
        if prediction.get("sentiment") == "bullish":
            sentiment_score = 1
        elif prediction.get("sentiment") == "bearish":
            sentiment_score = -1
            
        # Use statistical metrics for numerical analysis
        stats_score = 0
        if metrics.get("below_median_frequency", 0.5) < 0.4:
            # Price is frequently above median, potential uptrend
            stats_score += 0.5
        elif metrics.get("below_median_frequency", 0.5) > 0.6:
            # Price is frequently below median, potential downtrend
            stats_score -= 0.5
            
        # Volatility check - lower score for high volatility
        if metrics.get("volatility", 0.5) > 0.8:
            stats_score *= 0.7  # Reduce confidence for high volatility
            
        # Combine scores with weights
        # Following Rose Heart's advice on starting with equal weights
        final_score = (sentiment_score * 0.5) + (stats_score * 0.5)
        
        if final_score > 0.3:
            recommendation = "BUY"
            confidence = min(abs(final_score) * 100, 100)
        elif final_score < -0.3:
            recommendation = "SELL"
            confidence = min(abs(final_score) * 100, 100)
        else:
            recommendation = "HOLD"
            confidence = max(0, (1 - abs(final_score)) * 100)
            
        return {
            "action": recommendation,
            "confidence": confidence,
            "reasoning": f"Combined AI sentiment ({sentiment_score}) and statistical signals ({stats_score})"
        }
