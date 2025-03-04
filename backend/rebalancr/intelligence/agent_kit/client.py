from coinbase_agentkit import AgentKit, AgentKitConfig, CdpWalletProvider, CdpWalletProviderConfig
import asyncio
from typing import Dict, Any, Optional, TYPE_CHECKING
import aiohttp
import logging

from rebalancr.config import Settings

# Use conditional import to avoid circular imports
if TYPE_CHECKING:
    from ..intelligence_engine import IntelligenceEngine

logger = logging.getLogger(__name__)

from ..allora.client import AlloraClient
from ..market_analysis import MarketAnalyzer

class AgentKitClient:
    def __init__(self, config: Settings, intelligence_engine=None):
        # First create a wallet provider config
        wallet_provider_config = CdpWalletProviderConfig(
            api_key_name=config.CDP_API_KEY_NAME,
            api_key_private_key=config.CDP_API_KEY_PRIVATE_KEY
        )
        
        # Create the wallet provider
        self.wallet_provider = CdpWalletProvider(wallet_provider_config)
        
        # Create the AgentKit config
        agent_kit_config = AgentKitConfig(
            wallet_provider=self.wallet_provider,
            # Add other required parameters here
        )
        
        # Initialize AgentKit with the proper config
        self.agent_kit = AgentKit(agent_kit_config)
        
        self.conversations = {}  # Store active conversations
        
        # Initialize Allora client
        self.allora_client = AlloraClient(api_key=config.ALLORA_API_KEY)
        
        # Initialize market analyzer
        self.market_analyzer = MarketAnalyzer()
        
        # Initialize intelligence engine
        self.intelligence_engine = intelligence_engine
        self.base_url = "https://api.example.com/agentkit"  # Replace with actual URL
        
    def set_intelligence_engine(self, intelligence_engine):
        """Set the intelligence engine after initialization"""
        self.intelligence_engine = intelligence_engine
        
    async def initialize_session(self, user_id):
        """Initialize a new conversation for a user"""
        conversation = await self.agent_kit.create_conversation(user_id)
        self.conversations[user_id] = conversation.id
        return conversation.id
        
    async def send_message(self, user_id, message):
        """Send a message to the agent"""
        if user_id not in self.conversations:
            await self.initialize_session(user_id)
            
        return await self.agent_kit.send_message(
            conversation_id=self.conversations[user_id],
            content=message
        )
    
    async def process_chat_action(self, user_id, intent, parameters):
        """
        Process a chat action from a user, integrating Allora predictions
        and statistical analysis from Rose Heart's approach
        """
        if intent == "get_market_prediction":
            asset = parameters.get("asset", "BTC")
            topic_id = {"BTC": 14, "ETH": 13}.get(asset)
            
            if topic_id:
                try:
                    # Get Allora prediction
                    prediction = await self.allora_client.get_prediction(topic_id)
                    
                    # Combine with statistical analysis
                    # This follows Rose Heart's advice about using AI for sentiment
                    # but statistics for numerical analysis
                    historical_data = await self._get_historical_data(asset)
                    metrics = self.market_analyzer.calculate_asset_metrics(historical_data)
                    
                    # Combine insights (AI sentiment + statistical facts)
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
                            "technical_indicators": "Mixed signals" # Placeholder
                        },
                        "recommendation": self._generate_recommendation(prediction, metrics)
                    }
                    
                    return response
                except Exception as e:
                    return {"error": f"Failed to get prediction: {str(e)}"}
            else:
                return {"error": "Unsupported asset"}
                
        elif intent == "rebalance_portfolio":
            # Get user portfolio data
            user_info = await self.agent_kit.get_user_info(self.conversations[user_id])
            portfolio = await self._get_user_portfolio(user_info.wallet_address)
            current_prices = await self._get_current_prices(list(portfolio.keys()))
            historical_data = {
                asset: await self._get_historical_data(asset)
                for asset in portfolio
            }
            
            # Generate recommendation using strategy engine
            recommendation = await self.strategy_engine.generate_portfolio_recommendation(
                portfolio, current_prices, historical_data
            )
            
            # If rebalancing is recommended and profitable
            if recommendation["rebalance_analysis"]["recommendation"] == "rebalance":
                # Prepare the trades
                trades = recommendation["rebalance_analysis"]["trades"]
                
                # Execute trades through AgentKit
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
        
        # Handle other intents...
        return {"error": f"Unknown intent: {intent}"}
    
    async def execute_smart_contract(self, user_id, contract_address, function_name, args):
        """Execute a smart contract call via AgentKit"""
        if user_id not in self.conversations:
            await self.initialize_session(user_id)
            
        return await self.agent_kit.smart_contract_write(
            conversation_id=self.conversations[user_id],
            contract_address=contract_address,
            function_name=function_name,
            args=args
        )
    
    async def _get_user_portfolio(self, wallet_address):
        """Get user's current portfolio holdings"""
        # Implementation depends on your data sources
        pass
    
    async def _get_current_prices(self, assets):
        """Get current prices for assets"""
        # Implementation depends on your data sources
        pass
    
    async def _get_historical_data(self, asset):
        """Get historical data for statistical analysis"""
        # Implementation depends on your data sources
        pass
    
    def _generate_recommendation(self, prediction, metrics):
        """
        Generate a recommendation combining AI sentiment and statistical metrics
        Following Rose Heart's approach of using AI for sentiment and statistics for numbers
        """
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
