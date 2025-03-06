import asyncio
import logging
from ..api.websocket import connection_manager
from ..database.db_manager import DatabaseManager
from ..strategy.engine import StrategyEngine

logger = logging.getLogger(__name__)

async def monitor_portfolios(db_manager: DatabaseManager, strategy_engine: StrategyEngine):
    """Background task to monitor portfolios and trigger rebalancing when needed"""
    while True:
        try:
            # Get all active portfolios
            active_portfolios = await db_manager.get_active_portfolios()
            
            for portfolio in active_portfolios:
                user_id = portfolio['user_id']
                portfolio_id = portfolio['id']
                
                # Check if portfolio needs rebalancing
                analysis = await strategy_engine.analyze_rebalance_opportunity(user_id, portfolio_id)
                
                if analysis.get("rebalance_recommended", False):
                    # Notify user that rebalancing is recommended
                    await connection_manager.send_personal_message(
                        {
                            "type": "rebalance_recommendation",
                            "portfolio_id": portfolio_id,
                            "message": analysis.get("message", "Rebalancing is recommended.")
                        },
                        user_id
                    )
            
            # Wait before next check
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            logger.error(f"Error monitoring portfolios: {str(e)}")
            await asyncio.sleep(300)  # Wait and retry