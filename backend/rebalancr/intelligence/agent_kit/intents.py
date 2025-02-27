from coinbase_agentkit import create_intent

# Custom intents for financial actions
deposit_to_curvance = create_intent(
    name="deposit_to_curvance",
    description="Deposit assets to Curvance Universal Balance",
    parameters={
        "asset_address": {"type": "string", "description": "Address of the token to deposit"},
        "amount": {"type": "string", "description": "Amount to deposit in wei"}
    }
)

rebalance_portfolio = create_intent(
    name="rebalance_portfolio",
    description="Rebalance user portfolio based on current strategy",
    parameters={}
)
