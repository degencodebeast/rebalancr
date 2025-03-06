import asyncio
import aiohttp
from typing import Dict, List, Optional, Any

class AlloraClient:
    """Client for interacting with Allora Network APIs"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.allora.network"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        self.topic_map = {
            # Short-term predictions (5min)
            "ETH_5min": 13,
            "BTC_5min": 14,
            "ETH_5min_volatility": 15,
            "BTC_5min_volatility": 16,
            
            # Medium-term predictions
            "ETH_10min": 1,
            "BTC_10min": 3,
            "SOL_10min": 5,
            "ETH_20min": 7,
            "BNB_20min": 8,
            "ARB_20min": 9,
            
            # Long-term predictions (24h)
            "ETH_24h": 2,
            "BTC_24h": 4,
            "SOL_24h": 6,
            
            # Special topics
            "MEME_1h": 10
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_prediction(self, topic_id: int) -> Dict[str, Any]:
        """
        Get the latest prediction for a specific topic
        
        Args:
            topic_id: The Allora topic ID (e.g., 14 for BTC, 13 for ETH)
            
        Returns:
            Dictionary containing prediction data
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
            
        url = f"{self.base_url}/v1/topics/{topic_id}/predictions/latest"
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Failed to get prediction: {error_text}")
                
    async def get_market_sentiment(self, asset: str) -> Dict[str, Any]:
        """Get market sentiment analysis for an asset"""
        # Implementation depends on Allora's specific endpoints
        pass

    async def analyze_sentiment(self, asset: str, content: str) -> Dict[str, Any]:
        """
        Analyze sentiment for an asset from content (news, social media, etc.)
        
        Following Rose Heart's advice, this focuses ONLY on sentiment/emotion analysis
        
        Args:
            asset: Asset symbol (e.g., "BTC")
            content: Text content to analyze
            
        Returns:
            Dictionary with sentiment analysis and fear/greed classification
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
            
        url = f"{self.base_url}/v1/sentiment/analyze"
        async with self.session.post(url, json={
            "asset": asset,
            "content": content
        }) as response:
            if response.status == 200:
                result = await response.json()
                
                # Extract fear/greed signals as Rose Heart suggested
                fear_score = result.get("fear_score", 0.5)
                greed_score = result.get("greed_score", 0.5)
                
                # Check for manipulation attempts (Rose Heart's advice)
                manipulation_score = result.get("manipulation_score", 0.0)
                
                return {
                    "asset": asset,
                    "sentiment": result.get("sentiment", "neutral"),
                    "fear_score": fear_score,
                    "greed_score": greed_score,
                    "manipulation_detected": manipulation_score > 0.6,
                    "primary_emotion": "fear" if fear_score > greed_score else "greed"
                }
            else:
                error_text = await response.text()
                raise Exception(f"Failed to analyze sentiment: {error_text}")

    async def get_topic_prediction(self, topic_key: str, arg: Optional[str] = None) -> Dict[str, Any]:
        """
        Get prediction from an Allora topic
        
        Args:
            topic_key: Key from topic_map (e.g., "ETH_5min")
            arg: Optional argument to pass to the topic
        """
        if topic_key not in self.topic_map:
            raise ValueError(f"Unknown topic key: {topic_key}")
            
        topic_id = self.topic_map[topic_key]
        
        # Use default arg if none provided
        if arg is None:
            # Default args based on the topic documentation
            default_args = {
                "ETH_5min": "ETH",
                "BTC_5min": "BTC",
                "ETH_10min": "ETH",
                # ... add others as needed
            }
            arg = default_args.get(topic_key, "")
            
        # Ensure session is created
        if not self.session:
            self.session = aiohttp.ClientSession(headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
            
        url = f"{self.base_url}/v1/topics/{topic_id}/predictions"
        params = {"arg": arg} if arg else {}
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                error_text = await response.text()
                raise Exception(f"Failed to get prediction: {error_text}")
