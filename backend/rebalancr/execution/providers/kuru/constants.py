# Supported networks by Kuru
SUPPORTED_NETWORKS = {
    1: "Ethereum",
    8453: "Base",
    84532: "Base Sepolia",
}

# Default RPC URLs by chain ID
DEFAULT_RPC_URLS = {
    1: "https://ethereum.public-rpc.com",
    8453: "https://base.publicnode.com",
    84532: "https://sepolia.base.org",
}

# Token addresses on different networks
TOKEN_ADDRESSES = {
    8453: {  # Base
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "ETH": "0x0000000000000000000000000000000000000000",
        # Add more tokens as needed
    },
    84532: {  # Base Sepolia
        "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        "ETH": "0x0000000000000000000000000000000000000000",
        # Add more tokens as needed
    }
}