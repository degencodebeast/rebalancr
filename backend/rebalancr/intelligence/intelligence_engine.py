from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

import pandas as pd

from .allora.client import AlloraClient
from .market_analysis import MarketAnalyzer
from .agent_kit.client import AgentKitClient
from .market_data import MarketDataService

logger = logging.getLogger(__name__)

class IntelligenceEngine:
    #  Strategy engine that combines AI predictions from Allora
    # with statistical analysis as recommended by Rose Heart.
    """
    Strategy engine implementing Rose Heart's advice:
    - AI for sentiment analysis only
    - Statistical methods for numerical computations
    - Equal weighting to start (refined through testing)
    """
    
    def __init__(
        self, 
        allora_client: AlloraClient,
        market_analyzer: MarketAnalyzer,
        agent_kit_client: AgentKitClient,
        market_data_service: MarketDataService,
        config: Dict[str, Any]
    ):
        self.allora_client = allora_client
        self.market_analyzer = market_analyzer
        self.agent_kit_client = agent_kit_client
        self.market_data_service = market_data_service
        self.config = config

        #  # Map of assets to Allora topic IDs
        # self.topic_mappings = {
        #     "BTC": 14,
        #     "ETH": 13,
        #     # Add other assets as needed
        
        # Initial equal weights as Rose Heart suggested
        self.weights = {
            "sentiment": 0.25,
            "below_median": 0.25,
            "volatility": 0.25,
            "trend": 0.25
        }

    #            # Weights for different signals (statistical vs AI)
    #     # Starting with equal weights as Rose Heart suggested
    #     self.signal_weights = {
    #         "allora_prediction": 0.25,
    #         "statistical_metrics": 0.25,
    #         "market_sentiment": 0.25,
    #         "technical_indicators": 0.25
    #     }
        
    # async def generate_portfolio_recommendation(
    #     self,
    #     portfolio: Dict[str, float],
    #     current_prices: Dict[str, float],
    #     historical_data: Dict[str, Any]
    # ) -> Dict[str, Any]:
    
    async def analyze_portfolio(self, user_id: str, portfolio_id: int) -> Dict[str, Any]:
        # Generate portfolio recommendations using both AI and statistical methods
        """
        Analyze portfolio and determine if rebalancing is needed
        
        Implements the dual approach from Rose Heart:
        1. AI sentiment analysis for each asset
        2. Statistical analysis for each asset
        3. Combined with equal weights initially
        """
    #             # 1. Get Allora predictions for relevant assets
    #     allora_predictions = {}
    #     for asset, topic_id in self.topic_mappings.items():
    #         if asset in portfolio:
    #             try:
    #                 prediction = await self.allora_client.get_prediction(topic_id)
    #                 allora_predictions[asset] = prediction
    #             except Exception as e:
    #                 logger.error(f"Failed to get Allora prediction for {asset}: {e}")
        
    #     # 2. Perform statistical analysis
    #     asset_metrics = {}
    #     for asset in portfolio:
    #         if asset in historical_data:
    #             metrics = self.market_analyzer.calculate_asset_metrics(
    #                 historical_data[asset]
    #             )
    #             asset_metrics[asset] = metrics
        
    #     # 3. Calculate target weights using both inputs
    #     target_weights = self._calculate_target_weights(
    #         portfolio, 
    #         allora_predictions, 
    #         asset_metrics
    #     )
        
    #     # 4. Analyze rebalance opportunity
    #     rebalance_analysis = self.market_analyzer.analyze_rebalance_opportunity(
    #         portfolio,
    #         target_weights,
    #         current_prices,
    #         fee_rate=self.config.get("fee_rate", 0.001)
    #     )
        
    #     return {
    #         "target_weights": target_weights,
    #         "rebalance_analysis": rebalance_analysis,
    #         "allora_signals": allora_predictions,
    #         "statistical_signals": asset_metrics
    #     }
        
    # def _calculate_target_weights(
    #     self,
    #     portfolio: Dict[str, float],
    #     allora_predictions: Dict[str, Any],
    #     asset_metrics: Dict[str, Dict[str, float]]
    # ) -> Dict[str, float]:
    #     """
    #     Calculate target weights using both AI and statistical signals
    #     """
    #     # Implementation would combine signals with their respective weights
    #     # This is a simplified example
    #     assets = list(portfolio.keys())
    #     initial_weights = {asset: 1.0 / len(assets) for asset in assets}
        
    #     # Adjust weights based on signals
    #     adjusted_weights = initial_weights.copy()
        
    #     # Apply adjustments based on Allora predictions
    #     for asset in assets:
    #         if asset in allora_predictions:
    #             prediction = allora_predictions[asset]
    #             # Example: If prediction is bullish, increase weight
    #             if prediction.get("signal") == "bullish":
    #                 adjusted_weights[asset] *= 1.2
    #             elif prediction.get("signal") == "bearish":
    #                 adjusted_weights[asset] *= 0.8
        
    #     # Apply adjustments based on statistical metrics
    #     for asset in assets:
    #         if asset in asset_metrics:
    #             metrics = asset_metrics[asset]
    #             # Example: Adjust based on volatility
    #             volatility = metrics.get("volatility", 0.5)
    #             # Lower weight for higher volatility assets
    #             volatility_factor = 1.0 - ((volatility - 0.2) / 0.8)
    #             adjusted_weights[asset] *= max(0.5, min(1.5, volatility_factor))
        
    #     # Normalize weights to sum to 1.0
    #     total_weight = sum(adjusted_weights.values())
    #     normalized_weights = {
    #         asset: weight / total_weight for asset, weight in adjusted_weights.items()
    #     }
        
    #     return normalized_weights

        try:
            # Get portfolio data
            portfolio = await self.get_portfolio(user_id, portfolio_id)
            assets = portfolio.get("assets", [])
            
            # Rose Heart advised against rebalancing too frequently
            last_rebalance = portfolio.get("last_rebalance_timestamp")
            if last_rebalance:
                last_rebalance_date = datetime.fromisoformat(last_rebalance)
                days_since_rebalance = (datetime.now() - last_rebalance_date).days
                if days_since_rebalance < self.config.get("MIN_REBALANCE_DAYS", 7):
                    return {
                        "portfolio_id": portfolio_id,
                        "rebalance_needed": False,
                        "reason": f"Last rebalance was only {days_since_rebalance} days ago",
                        "message": "Too frequent rebalancing incurs unnecessary fees."
                    }
            
            # Get market data for all assets
            market_data = await self.market_data_service.get_data_for_assets(
                [asset["symbol"] for asset in assets]
            )
            
            # Process each asset
            results = []
            for asset in assets:
                symbol = asset["symbol"]
                
                # 1. Get AI sentiment analysis (fear/greed)
                # Rose Heart advised to focus AI only on sentiment
                sentiment_data = await self.allora_client.analyze_sentiment(
                    symbol, 
                    await self.market_data_service.get_social_content(symbol)
                )
                
                # 2. Get statistical analysis
                # Rose Heart advised to use traditional statistics for numbers
                stats_data = await self.market_analyzer.analyze_asset(
                    symbol,
                    market_data.get(symbol, pd.DataFrame())
                )
                
                # 3. Combine results with equal weights
                # Start with equal weights as Rose Heart suggested
                combined_score = 0.0
                
                # Sentiment contribution
                if sentiment_data.get("primary_emotion") == "greed":
                    combined_score += self.weights["sentiment"]
                elif sentiment_data.get("primary_emotion") == "fear":
                    combined_score -= self.weights["sentiment"]
                    
                # Below median frequency contribution
                below_median = stats_data.get("below_median_frequency", 0.5)
                if below_median < 0.4:  # Price frequently above median
                    combined_score += self.weights["below_median"]
                elif below_median > 0.6:  # Price frequently below median
                    combined_score -= self.weights["below_median"]
                
                # Volatility contribution - penalize high volatility
                volatility = stats_data.get("volatility", 0.5)
                if volatility > 0.8:  # High volatility
                    combined_score -= self.weights["volatility"]
                elif volatility < 0.3:  # Low volatility
                    combined_score += self.weights["volatility"]
                    
                # Trend contribution
                if stats_data.get("trend") == "uptrend":
                    combined_score += self.weights["trend"]
                else:
                    combined_score -= self.weights["trend"]
                    
                # Check for manipulation as Rose Heart advised
                if sentiment_data.get("manipulation_detected", False):
                    combined_score *= 0.5  # Reduce confidence if manipulation detected
                
                # Determine action
                action = "maintain"
                if combined_score > 0.3:
                    action = "increase"
                elif combined_score < -0.3:
                    action = "decrease"
                
                results.append({
                    "asset": symbol,
                    "current_allocation": asset.get("percentage", 0),
                    "recommended_action": action,
                    "confidence": abs(combined_score) * 100,
                    "sentiment": sentiment_data.get("primary_emotion"),
                    "statistical_signal": stats_data.get("statistical_signal"),
                    "manipulation_detected": sentiment_data.get("manipulation_detected", False)
                })
            
            # Determine if rebalancing is needed
            rebalance_needed = any(result["recommended_action"] != "maintain" for result in results)
            
            return {
                "portfolio_id": portfolio_id,
                "rebalance_needed": rebalance_needed,
                "assets": results,
                "message": "Rebalancing recommended" if rebalance_needed else "Portfolio is balanced"
            }
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {str(e)}")
            return {
                "portfolio_id": portfolio_id,
                "rebalance_needed": False,
                "error": str(e),
                "message": "Error analyzing portfolio"
            }
    
    async def get_portfolio(self, user_id: str, portfolio_id: int) -> Dict[str, Any]:
        """Get portfolio data from database or service"""
        # This would connect to your portfolio service or database
        # For now, returning dummy data
        return {
            "id": portfolio_id,
            "user_id": user_id,
            "name": "Test Portfolio",
            "last_rebalance_timestamp": "2023-04-01T12:00:00",
            "assets": [
                {"symbol": "BTC", "amount": 0.5, "percentage": 40},
                {"symbol": "ETH", "amount": 5.0, "percentage": 30},
                {"symbol": "SOL", "amount": 20.0, "percentage": 20},
                {"symbol": "USDC", "amount": 1000.0, "percentage": 10}
            ]
        }
