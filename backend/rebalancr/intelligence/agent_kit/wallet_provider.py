import os
import json
import base64
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from abc import ABC, abstractmethod

# Load environment variables
load_dotenv()

# Privy API configuration
PRIVY_APP_ID = os.getenv("PRIVY_APP_ID")
PRIVY_APP_SECRET = os.getenv("PRIVY_APP_SECRET")
PRIVY_WALLET_ID = os.getenv("PRIVY_WALLET_ID")  # Optional, will create a new wallet if not provided

# Configure a file to persist the wallet data
WALLET_DATA_FILE = "privy_wallet_data.json"

# Add the WalletProvider interface
class WalletProvider(ABC):
    """Abstract base class for wallet providers"""
    
    @abstractmethod
    async def get_wallet_address(self, user_id: str) -> Optional[str]:
        """Get the wallet address for a user"""
        pass
    
    @abstractmethod
    async def sign_transaction(self, user_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a transaction using the user's wallet"""
        pass
    
    @abstractmethod
    async def send_transaction(self, user_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a signed transaction to the blockchain"""
        pass
    
    @abstractmethod
    async def get_balance(self, user_id: str, token_address: Optional[str] = None) -> Dict[str, Any]:
        """Get the balance of the user's wallet"""
        pass

# Modify PrivyWalletProvider to implement WalletProvider
class PrivyWalletProvider(WalletProvider):
    """
    Custom wallet provider that uses Privy Server Wallets
    for integration with AgentKit.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None, db_manager=None):
        self.config = config or {}
        #self.wallet_id = self.config.get('wallet_id') or PRIVY_WALLET_ID or None
        self.wallet_id = None
        self.app_id = self.config.get('app_id') or PRIVY_APP_ID
        self.app_secret = self.config.get('app_secret') or PRIVY_APP_SECRET
        self.db_manager = db_manager
        
        # Validate required credentials
        if not self.app_id or not self.app_secret:
            raise ValueError("Missing Privy app credentials. Set PRIVY_APP_ID and PRIVY_APP_SECRET environment variables.")
        
        # Load existing wallet data if available
        self.wallet_data = self._load_wallet_data()
        
        # Create or fetch wallet
        if not self.wallet_id and not self.wallet_data.get('id'):
            self._create_wallet()
        elif self.wallet_id and not self.wallet_data.get('id'):
            self._fetch_wallet_by_id(self.wallet_id)
    
    def _load_wallet_data(self) -> Dict[str, Any]:
        """Load wallet data from file if it exists"""
        if os.path.exists(WALLET_DATA_FILE):
            try:
                with open(WALLET_DATA_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading wallet data: {str(e)}")
        return {}
    
    def _save_wallet_data(self):
        """Save wallet data to file"""
        try:
            with open(WALLET_DATA_FILE, 'w') as f:
                json.dump(self.wallet_data, f, indent=2)
        except Exception as e:
            print(f"Error saving wallet data: {str(e)}")
    
    def _get_auth_headers(self):
        """Get headers for Privy API authentication"""
        # Create Basic Auth header using app_id:app_secret
        auth_str = f"{self.app_id}:{self.app_secret}"
        basic_auth = base64.b64encode(auth_str.encode()).decode()
        
        return {
            "Content-Type": "application/json",
            "privy-app-id": self.app_id,
            "Authorization": f"Basic {basic_auth}"
        }
    
    def _create_wallet(self):
        """Create a new Privy wallet using REST API"""
        try:
            url = "https://api.privy.io/v1/wallets"
            headers = self._get_auth_headers()
            
            # According to Privy docs, for EVM wallets:
            data = {
                "chain_type": "ethereum"  # For EVM compatibility
            }
            
            # Make API call to create wallet
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            self.wallet_data = response.json()
            self.wallet_id = self.wallet_data.get("id")
            self._save_wallet_data()
            
            print(f"Created new Privy wallet with ID: {self.wallet_id} and address: {self.wallet_data.get('address')}")
            
        except Exception as e:
            print(f"Error creating Privy wallet: {str(e)}")
            raise
    
    def _fetch_wallet_by_id(self, wallet_id):
        """Fetch existing wallet details from Privy"""
        try:
            url = f"https://api.privy.io/v1/wallets/{wallet_id}"
            headers = self._get_auth_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            self.wallet_data = response.json()
            self._save_wallet_data()
            
        except Exception as e:
            print(f"Error fetching Privy wallet: {str(e)}")
            raise
    
    def export_wallet(self):
        """Export wallet data in AgentKit compatible format"""
        class WalletData:
            def __init__(self, data):
                self.data = data
            
            def to_dict(self):
                return self.data
        
        # Format wallet data for AgentKit compatibility
        exported_data = {
            "walletId": self.wallet_data.get("id"),
            "address": self.wallet_data.get("address"),
            "networkId": "base-sepolia",  # Default to base-sepolia for CDP
            "chainType": self.wallet_data.get("chain_type")
        }
        
        return WalletData(exported_data)
    
    # Implement WalletProvider interface methods
    async def get_wallet_address(self, user_id: str) -> Optional[str]:
        """Get wallet address for a user"""
        if self.db_manager:
            # Try to get user-specific wallet from the database
            user_wallet = await self.db_manager.get_agent_wallet(user_id)
            if user_wallet and user_wallet.get("wallet_id"):
                # Fetch up-to-date wallet info from Privy
                self._fetch_wallet_by_id(user_wallet.get("wallet_id"))
                return self.wallet_data.get("address")
        
        # Fallback to the default wallet if no user-specific wallet
        return self.wallet_data.get("address")
    
    async def sign_transaction(self, user_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a transaction using Privy API"""
        wallet_id = await self._get_wallet_id_for_user(user_id)
        if not wallet_id:
            raise ValueError("No wallet found for this user")
        
        try:
            url = f"https://api.privy.io/v1/wallets/{wallet_id}/sign"
            headers = self._get_auth_headers()
            
            # Format transaction data according to Privy's API requirements
            payload = {
                "data": transaction_data
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error signing transaction with Privy: {str(e)}")
            raise
    
    async def send_transaction(self, user_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a transaction using Privy API"""
        wallet_id = await self._get_wallet_id_for_user(user_id)
        if not wallet_id:
            raise ValueError("No wallet found for this user")
        
        try:
            url = f"https://api.privy.io/v1/wallets/{wallet_id}/send"
            headers = self._get_auth_headers()
            
            response = requests.post(url, headers=headers, json=transaction_data)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error sending transaction with Privy: {str(e)}")
            raise
    
    async def get_balance(self, user_id: str, token_address: Optional[str] = None) -> Dict[str, Any]:
        """Get wallet balance using blockchain provider"""
        address = await self.get_wallet_address(user_id)
        if not address:
            raise ValueError("No wallet found for this user")
        
        # For native ETH balance
        if not token_address:
            try:
                # This would need to be implemented based on your preferred blockchain provider
                # Placeholder implementation
                return {
                    "balance": "1.5 ETH",
                    "token": "ETH"
                }
            except Exception as e:
                print(f"Error getting wallet balance: {str(e)}")
                raise
        # For ERC20 tokens
        else:
            try:
                # This would need ERC20 contract interaction
                # Placeholder implementation
                return {
                    "balance": "100.0",
                    "token": token_address
                }
            except Exception as e:
                print(f"Error getting token balance: {str(e)}")
                raise
    
    # Helper method for user-wallet mapping
    async def _get_wallet_id_for_user(self, user_id: str) -> Optional[str]:
        """Get the Privy wallet ID associated with a user"""
        if self.db_manager:
            user_wallet = await self.db_manager.get_agent_wallet(user_id)
            if user_wallet and user_wallet.get("wallet_id"):
                return user_wallet.get("wallet_id")
        
        # Fallback to default wallet
        return self.wallet_id


def get_wallet_provider() -> PrivyWalletProvider:
    """
    Factory function to create and return a configured Privy wallet provider
    for use with AgentKit.
    
    Returns:
        PrivyWalletProvider: Configured wallet provider instance
    """
    return PrivyWalletProvider()


def get_wallet_address(wallet_provider: Optional[PrivyWalletProvider] = None) -> str:
    """
    Get the wallet address from the wallet provider.
    
    Args:
        wallet_provider: Optional provider, will create one if not provided
        
    Returns:
        str: Wallet address
    """
    if wallet_provider is None:
        wallet_provider = get_wallet_provider()
    
    return wallet_provider.get_address()


def get_network_id(wallet_provider: Optional[PrivyWalletProvider] = None) -> str:
    """
    Get the network ID from the wallet provider.
    
    Args:
        wallet_provider: Optional provider, will create one if not provided
        
    Returns:
        str: Network ID (e.g., 'base-sepolia')
    """
    if wallet_provider is None:
        wallet_provider = get_wallet_provider()
    
    return wallet_provider.get_network_id() 