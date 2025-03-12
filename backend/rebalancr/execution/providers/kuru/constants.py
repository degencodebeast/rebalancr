"""Constants for Kuru action provider."""
import json
import os
from pathlib import Path

# Load ABI from JSON file
def load_abi(filename):
    """Load ABI from JSON file"""
    current_dir = Path(__file__).parent
    abi_path = current_dir / "abis" / filename
    try:
        with open(abi_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load ABI file {filename}: {e}")
        return []

# Contract addresses for Monad testnet (chain_id: 10143)
KURU_CONTRACT_ADDRESSES = {
    10143: {  # Monad testnet
        "ROUTER": "0xc816865f172d640d93712C68a7E1F83F3fA63235",
        "MARGIN_ACCOUNT": "0x4B186949F31FCA0aD08497Df9169a6bEbF0e26ef",
        "KURU_FORWARDER": "0x350678D87BAa7f513B262B7273ad8Ccec6FF0f78",
        "KURU_DEPLOYER": "0x67a4e43C7Ce69e24d495A39c43489BC7070f009B",
        "KURU_UTILS": "0x9E50D9202bec0D046a75048Be8d51bBa93386Ade"
    }
}

# Market addresses for Monad testnet
KURU_MARKET_ADDRESSES = {
    10143: {  # Monad testnet
        "MON_USDC": "0xd3af145f1aa1a471b5f0f62c52cf8fcdc9ab55d3",
        "DAK_MON": "0x94b72620e65577de5fb2b8a8b93328caf6ca161b"
    }
}

# Token addresses for Monad testnet
TOKEN_ADDRESSES = {
    "ETH": "0x0000000000000000000000000000000000000000",
    "WETH": {
        10143: "0x4200000000000000000000000000000000000006"
    },
    "USDC": {
        10143: "0xf817257fed379853cDe0fa4F97AB987181B1E5Ea"
    },
    "kUSDC": {
        10143: "0xf817257fed379853cDe0fa4F97AB987181B1E5Ea"
    },
    "USDT": {
        10143: "0x88b8E2161DEDC77EF4ab7585569D2415a1C1055D"
    },
    "DAK": {
        10143: "0x0F0BDEbF0F83cD1EE3974779Bcb7315f9808c714"
    }
}

# Load ABIs from existing JSON files in the abis directory
MARGIN_ACCOUNT_ABI = load_abi('margin_account.json')
KURU_MARKET_ABI = load_abi('order_book.json')
KURU_FORWARDER_ABI = load_abi('kuru_forwarder.json')
IERC20_ABI = load_abi('ierc20.json')

# Aliases for compatibility
ERC20_ABI = IERC20_ABI

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

# Add this definition
DEFAULT_RPC_URLS = {
    "42161": "https://arb1.arbitrum.io/rpc",  # Arbitrum One
    "421613": "https://goerli-rollup.arbitrum.io/rpc",  # Arbitrum Goerli
    "1": "https://eth.llamarpc.com",  # Ethereum Mainnet
    "5": "https://rpc.ankr.com/eth_goerli",  # Ethereum Goerli
    "535037": "https://rpc.testnet.monad.xyz",  # Monad Testnet
}