from typing import Dict, Any, Optional, TYPE_CHECKING
import asyncio
import aiohttp
import logging

from rebalancr.config import Settings
from ..allora.client import AlloraClient
from ..market_analysis import MarketAnalyzer
from .service import AgentKitService

# Use conditional import to avoid circular imports
if TYPE_CHECKING:
    from ..intelligence_engine import IntelligenceEngine

logger = logging.getLogger(__name__)

class AgentKitClient:
    """
    Client for AgentKit that implements business logic and domain operations.
    Uses AgentKitService for core infrastructure operations.
    Manages conversations, integrations with other services, and implements
    portfolio-specific operations.
    """
    def __init__(self, config: Settings, intelligence_engine=None):
        """Initialize the client with references to required services."""
        # Get the AgentKit service singleton
        self.service = AgentKitService.get_instance(config)
        
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
        
    async def send_message(self, user_id, message):
        """Send a message to the agent"""
        if user_id not in self.conversations:
            await self.initialize_session(user_id)
            
        return await self.service.send_message(
            conversation_id=self.conversations[user_id],
            content=message
        )
    
    async def process_chat_action(self, user_id, intent, parameters):
        """
        Process a chat action from a user, integrating Allora predictions
        and statistical analysis.
        """
        # Ensure user has a conversation
        if user_id not in self.conversations:
            await self.initialize_session(user_id)
            
        # Handle different intents with domain-specific logic
        if intent == "get_market_prediction":
            return await self._handle_market_prediction(user_id, parameters)
        elif intent == "rebalance_portfolio":
            return await self._handle_portfolio_rebalance(user_id, parameters)
        else:
            return {"error": f"Unknown intent: {intent}"}
    
    async def execute_smart_contract(self, user_id, contract_address, function_name, args):
        """Execute a smart contract call via AgentKit"""
        if user_id not in self.conversations:
            await self.initialize_session(user_id)
            
        return await self.service.execute_smart_contract(
            conversation_id=self.conversations[user_id],
            contract_address=contract_address,
            function_name=function_name,
            args=args
        )
    
    # Domain-specific operations
    
    async def _handle_market_prediction(self, user_id, parameters):
        """Handle market prediction logic"""
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
        """Handle portfolio rebalancing logic"""
        try:
            # Get user info and portfolio data
            conversation_id = self.conversations[user_id]
            user_info = await self.service.get_user_info(conversation_id)
            portfolio = await self._get_user_portfolio(user_info.wallet_address)
            
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

            # Generate recommendation 
            recommendation = await self.intelligence_engine.generate_portfolio_recommendation(
                portfolio, current_prices, historical_data
            )
            
            # If rebalancing is recommended and profitable
            if recommendation["rebalance_analysis"]["recommendation"] == "rebalance":
                # Execute trades
                trades = recommendation["rebalance_analysis"]["trades"]

    #                         asset = parameters.get("asset", "BTC")
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
    
    # async def execute_smart_contract(self, user_id, contract_address, function_name, args):
    #     """Execute a smart contract call via AgentKit"""
    #     if user_id not in self.conversations:
    #         await self.initialize_session(user_id)
            
    #     return await self.agent_kit.smart_contract_write(
    #         conversation_id=self.conversations[user_id],
    #         contract_address=contract_address,
    #         function_name=function_name,
    #         args=args
    #     )

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
    
    async def _execute_trades(self, user_id, trades):
        """Execute a set of trades for portfolio rebalancing"""
        results = []
        for asset, amount in trades.items():
            if amount > 0:  # Buy
                result = await self.execute_smart_contract(
                    user_id,
                    "DEX_CONTRACT_ADDRESS",
                    "buy",
                    [asset, str(abs(amount))]
                )
            else:  # Sell
                result = await self.execute_smart_contract(
                    user_id,
                    "DEX_CONTRACT_ADDRESS",
                    "sell",
                    [asset, str(abs(amount))]
                )
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

    async def execute_trade(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade via AgentKit"""
        # Implementation
        logger.info(f"Executing trade with params: {params}")
        return {"status": "success", "transaction_id": "dummy_id"}
    
    async def get_wallet_info(self, address: str) -> Dict[str, Any]:
        """Get wallet information"""
        # Implementation
        return {"address": address, "balance": 1000}
