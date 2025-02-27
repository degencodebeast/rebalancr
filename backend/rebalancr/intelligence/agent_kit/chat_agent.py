import os
import logging
from typing import Dict, List, Any, AsyncGenerator

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    wallet_action_provider,
    erc20_action_provider,
    pyth_action_provider,
    weth_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools

from ..allora.client import AlloraClient

logger = logging.getLogger(__name__)

class PortfolioAgent:
    """
    Agent integration using Coinbase AgentKit for portfolio management
    
    Handles chat interactions and executes commands using the AgentKit
    """
    # def __init__(self, 
    #              allora_client: AlloraClient, 
    #              wallet_provider, 
    #              config: Dict[str, Any]):
    def __init__(self, allora_client, db_manager, strategy_engine, wallet_provider=None):
        self.allora_client = allora_client
        self.db_manager = db_manager
        self.strategy_engine = strategy_engine
        self.wallet_provider = wallet_provider
        # self.config = config
        # self.memory = MemorySaver()
        
        # # Initialize the agent
        # self.agent, self.agent_config = self._initialize_agent()
        
    async def process_message(self, user_id, message, conversation_id=None):
        """Process a user message and generate appropriate responses"""
        # Basic message analysis to determine intent
        intent = await self._analyze_intent(message)
        
        # Handle all read-only operations regardless of wallet state
        if intent in ["market_info", "education", "analysis", "recommendation"]:
            async for response in self._handle_informational_request(user_id, message, intent):
                yield response
            return
            
        # Check if this requires on-chain actions
        if intent in ["execute_trade", "rebalance", "transfer", "approve"]:
            # Check if user has an agent wallet
            has_wallet = await self._user_has_agent_wallet(user_id)
            
            if not has_wallet:
                # Suggest wallet activation instead of executing action
                yield {
                    "type": "agent_message",
                    "content": "I'd like to help you execute this action, but I need permission first. "
                              "Please activate the agent wallet feature in your settings to enable me "
                              "to perform transactions on your behalf. In the meantime, here's what I would do..."
                }
                
                # Provide recommendation of what would happen if executed
                async for response in self._generate_action_preview(user_id, message, intent):
                    yield response
            else:
                # User has wallet, proceed with execution
                async for response in self._execute_on_chain_action(user_id, message, intent):
                    yield response
    
    async def _user_has_agent_wallet(self, user_id):
        """Check if user has activated an agent wallet"""
        wallet_info = await self.db_manager.get_agent_wallet(user_id)
        return wallet_info is not None
    
    # Other methods (handling different intents, etc.)
        
    def _initialize_agent(self):
        """Initialize the AgentKit React agent with necessary tools"""
        # Initialize LLM
        llm = ChatOpenAI(model=self.config.get("model", "gpt-4o-mini"))
        
        # Initialize AgentKit
        agentkit = AgentKit(AgentKitConfig(
            wallet_provider=self.wallet_provider,
            action_providers=[
                erc20_action_provider(),  # ERC20 token actions
                pyth_action_provider(),   # Price feeds
                wallet_action_provider(), # Wallet operations
                weth_action_provider(),   # WETH-specific operations
            ]
        ))
        
        # Get tools for LangChain integration
        tools = get_langchain_tools(agentkit)
        
        # Create agent configuration
        agent_config = {"configurable": {"thread_id": "Portfolio Rebalancing Agent"}}
        
        # Create and return the agent with tools
        agent = create_react_agent(
            llm,
            tools=tools,
            checkpointer=self.memory,
            state_modifier=(
                "You are a helpful portfolio rebalancing agent that can interact onchain "
                "using blockchain wallets. You can analyze sentiment, perform statistical "
                "analysis, and execute trades to rebalance portfolios. Always be clear about "
                "fees and risks before executing trades."
            ),
        )
        
        return agent, agent_config
    
        # async def process_message(self, 
        #                 user_id: str, 
        #                 message: str, 
        #                 conversation_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        # """
        # Process a user message and return agent responses
    
    async def _execute_on_chain_action(self, user_id, message, intent):
        """Handle execution of on-chain actions like trades"""

                # Yields chunks of the response as they become available
        # """
        # try:
        #     # Stream responses from the agent
        #     async for chunk in self.agent.stream(
        #         {"messages": [HumanMessage(content=message)]}, 
        #         self.agent_config
        #     ):
        #         if "agent" in chunk:
        #             yield {
        #                 "type": "agent_response",
        #                 "content": chunk["agent"]["messages"][0].content,
        #                 "conversation_id": conversation_id
        #             }
        #         elif "tools" in chunk:
        #             yield {
        #                 "type": "tool_execution",
        #                 "content": chunk["tools"]["messages"][0].content,
        #                 "conversation_id": conversation_id
        #             }
        # except Exception as e:
        #     logger.error(f"Error processing message: {str(e)}")
        #     yield {
        #         "type": "error",
        #         "content": f"There was an error processing your request: {str(e)}",
        #         "conversation_id": conversation_id
        #     }
            
        # Extract trade parameters from message using NLP
        trade_params = await self._extract_trade_parameters(message)
        
        # Call TradeAgent to execute the trade
        result = await self.trade_agent.execute_trade(
            user_id=user_id,
            asset=trade_params['asset'],
            amount=trade_params['amount'],
            action=trade_params['action']
        )
        
        # Format response based on trade result
        if result['success']:
            yield {
                "type": "agent_message",
                "content": f"I've executed your trade: {result['message']}"
            }
            yield {
                "type": "transaction_receipt",
                "content": result
            }
        else:
            yield {
                "type": "agent_message",
                "content": f"I encountered an issue: {result['message']}"
            }
    
    async def chat(self, 
                  user_id: str, 
                  message: str, 
                  conversation_id: str = None) -> AsyncGenerator[str, None]:
        """
        Process a user message and return text responses
        
        This is a simplified version of process_message that only yields
        the text content of responses, for easier integration with the chat service.
        
        Args:
            user_id: User identifier
            message: User message content
            conversation_id: Optional conversation ID
            
        Yields:
            Text chunks of the response
        """
        async for response in self.process_message(user_id, message, conversation_id):
            # Only yield the content, not the full response object
            yield response["content"] 