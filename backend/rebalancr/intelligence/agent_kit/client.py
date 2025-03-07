from typing import Dict, Any, Optional, TYPE_CHECKING
import asyncio
import aiohttp
import logging

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
        
    async def send_message(self, user_id, message, session_id=None):
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
    
    async def process_chat_action(self, user_id, intent, parameters, session_id=None):
        """
        Process a domain-specific chat action from a user
        
        This method handles business operations such as:
        - Market predictions with Allora integration
        - Portfolio rebalancing with statistical analysis
        - Other domain-specific workflows
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
        """Handle market prediction logic with Allora integration"""
        asset = parameters.get("asset", "BTC")
        topic_id = {"BTC": 14, "ETH": 13}.get(asset)
        
        if not topic_id:
            return {"error": "Unsupported asset"}
        
        #             if topic_id:
        #         try:
        #             # Get Allora prediction
        #             prediction = await self.allora_client.get_prediction(topic_id)
                    
        #             # Combine with statistical analysis
        #             # This follows Rose Heart's advice about using AI for sentiment
        #             # but statistics for numerical analysis
        #             historical_data = await self._get_historical_data(asset)
        #             metrics = self.market_analyzer.calculate_asset_metrics(historical_data)
                    
        #             # Combine insights (AI sentiment + statistical facts)
        #             response = {
        #                 "message": f"Analysis for {asset}:",
        #                 "prediction": {
        #                     "sentiment": prediction.get("sentiment", "neutral"),
        #                     "direction": prediction.get("direction", "sideways"),
        #                     "confidence": prediction.get("confidence", 0.5),
        #                 },
        #                 "statistics": {
        #                     "volatility": metrics.get("volatility"),
        #                     "current_vs_median": metrics.get("below_median_frequency"),
        #                     "technical_indicators": "Mixed signals" # Placeholder
        #                 },
        #                 "recommendation": self._generate_recommendation(prediction, metrics)
        #             }
                    
        #             return response
        #         except Exception as e:
        #             return {"error": f"Failed to get prediction: {str(e)}"}
        #     else:
        #         return {"error": "Unsupported asset"}
                
        # elif intent == "rebalance_portfolio":
        #     # Get user portfolio data
        #     user_info = await self.agent_kit.get_user_info(self.conversations[user_id])
            
        try:
            # Get Allora prediction
            prediction = await self.allora_client.get_prediction(topic_id)
            
            # Combine with statistical analysis
            historical_data = await self._get_historical_data(asset)
            metrics = self.market_analyzer.calculate_asset_metrics(historical_data)
            
            # Combine insights
            response = {
                "message": f"Analysis for {asset}:",
                "prediction": {
                    "sentiment": prediction.get("sentiment", "neutral"),
                    "direction": prediction.get("direction", "sideways"),
                    "confidence": prediction.get("confidence", 0.5),
                },
                "statistics": {
                    "volatility": metrics.get("volatility"),
                    "current_vs_median": metrics.get("below_median_frequency"),
                    "technical_indicators": "Mixed signals"
                },
                "recommendation": self._generate_recommendation(prediction, metrics)
            }
            
            return response
        except Exception as e:
            logger.error(f"Error getting market prediction: {str(e)}")
            return {"error": f"Failed to get prediction: {str(e)}"}
    
    async def _handle_portfolio_rebalance(self, user_id, parameters):
        """Handle portfolio rebalancing with statistical analysis"""
        #   """Handle portfolio rebalancing logic"""
        try:
            # Get user info through AgentManager to ensure wallet data is loaded
            async with self.agent_manager.get_agent_executor(user_id) as agent:
                wallet_info_result = await agent.ainvoke({"messages": ["What is my wallet address?"]})
                # Extract wallet address from result
                wallet_address = self._extract_wallet_address(wallet_info_result)
            
            # Get portfolio data
            portfolio = await self._get_user_portfolio(wallet_address)
            
            if not portfolio:
                return {"message": "No portfolio found for this user"}
                
            # Get market data
            current_prices = await self._get_current_prices(list(portfolio.keys()))
            historical_data = {
                asset: await self._get_historical_data(asset)
                for asset in portfolio
            }

            # # Generate recommendation using strategy engine
            # recommendation = await self.strategy_engine.generate_portfolio_recommendation(

            # Generate recommendation using intelligence engine
            recommendation = await self.intelligence_engine.generate_portfolio_recommendation(
                portfolio, current_prices, historical_data
            )
            
            # If rebalancing is recommended and profitable
            if recommendation["rebalance_analysis"]["recommendation"] == "rebalance":
                # Execute trades through AgentManager
                trades = recommendation["rebalance_analysis"]["trades"]

                
    #         asset = parameters.get("asset", "BTC")
    #         topic_id = {"BTC": 14, "ETH": 13}.get(asset)
            
    #         if topic_id:
    #             try:
    #                 # Get Allora prediction
    #                 prediction = await self.allora_client.get_prediction(topic_id)
                    
    #                 # Combine with statistical analysis
    #                 # This follows Rose Heart's advice about using AI for sentiment
    #                 # but statistics for numerical analysis
    #                 historical_data = await self._get_historical_data(asset)
    #                 metrics = self.market_analyzer.calculate_asset_metrics(historical_data)
                    
    #                 # Combine insights (AI sentiment + statistical facts)
    #                 response = {
    #                     "message": f"Analysis for {asset}:",
    #                     "prediction": {
    #                         "sentiment": prediction.get("sentiment", "neutral"),
    #                         "direction": prediction.get("direction", "sideways"),
    #                         "confidence": prediction.get("confidence", 0.5),
    #                     },
    #                     "statistics": {
    #                         "volatility": metrics.get("volatility"),
    #                         "current_vs_median": metrics.get("below_median_frequency"),
    #                         "technical_indicators": "Mixed signals" # Placeholder
    #                     },
    #                     "recommendation": self._generate_recommendation(prediction, metrics)
    #                 }
                    
    #                 return response
    #             except Exception as e:
    #                 return {"error": f"Failed to get prediction: {str(e)}"}
    #         else:
    #             return {"error": "Unsupported asset"}
                
    #     elif intent == "rebalance_portfolio":
    #         # Get user portfolio data
    #         user_info = await self.agent_kit.get_user_info(self.conversations[user_id])
    #         # Generate recommendation using strategy engine
    #         recommendation = await self.strategy_engine.generate_portfolio_recommendation(
    #         # If rebalancing is recommended and profitable
    #             # Prepare the trades
                
    #             # Execute trades through AgentKit
    #             results = []
    #             for asset, amount in trades.items():
    #                 if amount > 0:  # Buy
    #                     result = await self.execute_smart_contract(
    #                         user_id,
    #                         "DEX_CONTRACT_ADDRESS",
    #                         "buy",
    #                         [asset, str(abs(amount))]
    #                     )
    #                 else:  # Sell
    #                     result = await self.execute_smart_contract(
    #                         user_id,
    #                         "DEX_CONTRACT_ADDRESS",
    #                         "sell",
    #                         [asset, str(abs(amount))]
    #                     )
    #                 results.append(result)
                
    #             return {
    #                 "message": "Portfolio rebalancing complete",
    #                 "trades_executed": len(results),
    #                 "new_weights": recommendation["target_weights"]
    #             }
    #         else:
    #             return {
    #                 "message": "Rebalancing not recommended at this time",
    #                 "reason": "Fees would exceed expected benefits",
    #                 "current_weights": recommendation["rebalance_analysis"]["current_weights"]
    #             }
        
    #     # Handle other intents...
    #     return {"error": f"Unknown intent: {intent}"}


                results = await self._execute_trades(user_id, trades)
                
                return {
                    "message": "Portfolio rebalancing complete",
                    "trades_executed": len(results),
                    "new_weights": recommendation["target_weights"]
                }
            else:
                return {
                    "message": "Rebalancing not recommended at this time",
                    "reason": "Fees would exceed expected benefits",
                    "current_weights": recommendation["rebalance_analysis"]["current_weights"]
                }
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
