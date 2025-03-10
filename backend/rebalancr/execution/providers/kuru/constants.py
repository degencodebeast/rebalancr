# # Supported networks by Kuru
# SUPPORTED_NETWORKS = {
#     1: "Ethereum",
#     8453: "Base",
#     84532: "Base Sepolia",
# }

# # Default RPC URLs by chain ID
# DEFAULT_RPC_URLS = {
#     1: "https://ethereum.public-rpc.com",
#     8453: "https://base.publicnode.com",
#     84532: "https://sepolia.base.org",
# }

# # Token addresses on different networks
# TOKEN_ADDRESSES = {
#     8453: {  # Base
#         "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
#         "ETH": "0x0000000000000000000000000000000000000000",
#         # Add more tokens as needed
#     },
#     84532: {  # Base Sepolia
#         "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
#         "ETH": "0x0000000000000000000000000000000000000000",
#         # Add more tokens as needed
#     }
# }

"""Constants for Kuru action provider."""

# Default RPC URLs for supported networks
DEFAULT_RPC_URLS = {
    8453: "https://base-mainnet.public.blastapi.io",
    84532: "https://sepolia.base.org"
}

# Token addresses
TOKEN_ADDRESSES = {
    "ETH": "0x0000000000000000000000000000000000000000",
    "WETH": {
        8453: "0x4200000000000000000000000000000000000006",
        84532: "0x4200000000000000000000000000000000000006"
    },
    "USDC": {
        8453: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        84532: "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
    }
}

# Kuru Market ABI (simplified example - this would need to be filled with actual ABI)
KURU_MARKET_ABI = [
    {
        "inputs": [
            {"internalType": "uint8", "name": "side", "type": "uint8"},
            {"internalType": "uint256", "name": "price", "type": "uint256"},
            {"internalType": "uint256", "name": "size", "type": "uint256"},
            {"internalType": "uint8", "name": "orderType", "type": "uint8"},
            {"internalType": "uint8", "name": "postOnly", "type": "uint8"},
            {"internalType": "uint256", "name": "minAmountOut", "type": "uint256"},
            {"internalType": "string", "name": "cloid", "type": "string"}
        ],
        "name": "createOrder",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "cloid", "type": "string"}
        ],
        "name": "cancelOrder",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint8[]", "name": "sides", "type": "uint8[]"},
            {"internalType": "uint256[]", "name": "prices", "type": "uint256[]"},
            {"internalType": "uint256[]", "name": "sizes", "type": "uint256[]"},
            {"internalType": "uint8[]", "name": "orderTypes", "type": "uint8[]"},
            {"internalType": "uint8[]", "name": "postOnlys", "type": "uint8[]"},
            {"internalType": "uint256[]", "name": "minAmountsOut", "type": "uint256[]"},
            {"internalType": "string[]", "name": "cloids", "type": "string[]"}
        ],
        "name": "batchOrders",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
            # ... continued from previous response ...
    },
    {
        "inputs": [],
        "name": "getBids",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "price", "type": "uint256"},
                    {"internalType": "uint256", "name": "size", "type": "uint256"},
                    {"internalType": "string", "name": "orderId", "type": "string"}
                ],
                "internalType": "struct OrderInfo[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getAsks",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "price", "type": "uint256"},
                    {"internalType": "uint256", "name": "size", "type": "uint256"},
                    {"internalType": "string", "name": "orderId", "type": "string"}
                ],
                "internalType": "struct OrderInfo[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "orderId", "type": "string"}
        ],
        "name": "getOrderStatus",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint8", "name": "status", "type": "uint8"},
                    {"internalType": "uint256", "name": "filledSize", "type": "uint256"},
                    {"internalType": "uint256", "name": "remainingSize", "type": "uint256"},
                    {"internalType": "uint256", "name": "price", "type": "uint256"}
                ],
                "internalType": "struct OrderStatus",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Kuru Router ABI (simplified example)
KURU_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "tokenIn", "type": "address"},
            {"internalType": "address", "name": "tokenOut", "type": "address"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Kuru Margin Account ABI (simplified example)
KURU_MARGIN_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"}
        ],
        "name": "tokenBalances",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC20 token ABI (for approvals)
ERC20_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "account", "type": "address"}
        ],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]