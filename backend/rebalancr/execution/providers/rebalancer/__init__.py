"""
Rebalancer Action Provider

This module provides actions for portfolio rebalancing, implementing the multi-layered
architecture that combines:
- AI sentiment analysis from Allora
- Statistical analysis from traditional financial methods
- Validation layer for trade approval
"""

# Don't import directly here
# from .rebalancer_action_provider import (
#    rebalancer_action_provider,
#    RebalancerActionProvider
# )

# Instead, expose a function that allows late importing
def get_rebalancer_provider():
    from .rebalancer_action_provider import rebalancer_action_provider
    return rebalancer_action_provider

# Export only the function
__all__ = ["get_rebalancer_provider"] 