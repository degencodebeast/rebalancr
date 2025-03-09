from .intents import deposit_to_curvance, rebalance_portfolio
from .handlers import handle_deposit_to_curvance, handle_rebalance_portfolio

# Map intent names to the corresponding handler function.
INTENT_HANDLER_MAP = {
    deposit_to_curvance.name: handle_deposit_to_curvance,
    rebalance_portfolio.name: handle_rebalance_portfolio,
}