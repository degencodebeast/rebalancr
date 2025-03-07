# import os
# import logging
# import json
# from typing import Dict, List, Any, AsyncGenerator, Optional

# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from langchain_openai import ChatOpenAI
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.prebuilt import create_react_agent

# from coinbase_agentkit import (
#     AgentKit,
#     AgentKitConfig,
#     wallet_action_provider,
#     erc20_action_provider,
#     pyth_action_provider,
#     weth_action_provider,
# )
# from coinbase_agentkit_langchain import get_langchain_tools
# from rebalancr.config import Settings

# from ..allora.client import AlloraClient
# from ...execution.action_registry import ActionRegistry
# from ..agent_kit.service import AgentKitService

# logger = logging.getLogger(__name__)

# class PortfolioAgent:
#     """
#     """
#     def __init__(self, 
#                  allora_client: AlloraClient, 
#                  db_manager, 
#                  strategy_engine,
#                  config: Settings,
#                  action_registry: ActionRegistry,
#                  wallet_provider=None):
#         self.allora_client = allora_client
#         self.db_manager = db_manager
#         self.strategy_engine = strategy_engine
#         self.action_registry = action_registry
#         self.wallet_provider = wallet_provider
#         self.config = config
#         # self.memory = MemorySaver()

#         # # Initialize the agent
#         # self.agent, self.agent_config = self._initialize_agent()
        
#         # Initialize LLM for intent detection
#         # api_key = os.environ.get("OPENAI_API_KEY")
#         # self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)
        
#         # Initialize the agent
#         self.agent_kit = AgentKitService.get_instance(config).agent_kit
        
#     async def process_message(self, user_id, message, conversation_id=None):
#         """Process a user message and generate appropriate responses"""

#         # # Basic message analysis to determine intent
#         # intent = await self._analyze_intent(message)
        
#         #  # Handle all read-only operations regardless of wallet state
#         # if intent in ["market_info", "education", "analysis", "recommendation"]:
#         #     async for response in self._handle_informational_request(user_id, message, intent):
#         #         yield response
#         #     return

#         # First, check if the message contains an intent to execute an action
#         intent_analysis = await self._analyze_intent(message)
        
#         if intent_analysis["type"] == "action":
#             # Execute the action
#             action_name = intent_analysis["action_name"]
#             action_params = intent_analysis["parameters"]
            
#             yield {
#                 "type": "agent_message",
#                 "content": f"I'll help you {intent_analysis['description']}."
#             }
            
#             # Check if user has a connected wallet for actions that require it
#             if self._action_requires_wallet(action_name) and not await self._user_has_agent_wallet(user_id):
#                 yield {
#                     "type": "agent_message",
#                     "content": "You'll need to connect a wallet before I can execute this action."
#                 }
                
#                 yield {
#                     "type": "wallet_request",
#                     "content": {
#                         "action": action_name,
#                         "parameters": action_params
#                     }
#                 }
#                 return
            
#         # # Check if this requires on-chain actions
#         # if intent in ["execute_trade", "rebalance", "transfer", "approve"]:
#         #     # Check if user has an agent wallet
#         #     has_wallet = await self._user_has_agent_wallet(user_id)
            
#             # Add user_id to params
#             action_params["user_id"] = user_id

#             #     if not has_wallet:
#             #     # Suggest wallet activation instead of executing action
#             #     yield {
#             #         "type": "agent_message",
#             #         "content": "I'd like to help you execute this action, but I need permission first. "
#             #                   "Please activate the agent wallet feature in your settings to enable me "
#             #                   "to perform transactions on your behalf. In the meantime, here's what I would do..."
#             #     }
                
#             #     # Provide recommendation of what would happen if executed
#             #     async for response in self._generate_action_preview(user_id, message, intent):
#             #         yield response
#             # else:
#             #     # User has wallet, proceed with execution
#             #     async for response in self._execute_on_chain_action(user_id, message, intent):
#             #         yield response
            
#             try:
#                 # Get the action from registry and execute it
#                 action = self.action_registry.get_action(action_name)
#                 result = await action.execute(**action_params)
                
#                 # Return result
#                 if result.get("success", False):
#                     yield {
#                         "type": "agent_message",
#                         "content": f"✅ {result.get('message', 'Action completed successfully.')}"
#                     }
                    
#                     yield {
#                         "type": "action_result",
#                         "content": result
#                     }
#                 else:
#                     yield {
#                         "type": "agent_message",
#                         "content": f"❌ {result.get('message', 'Action failed.')}"
#                     }
#             except Exception as e:
#                 logger.error(f"Error executing action {action_name}: {str(e)}")
#                 yield {
#                     "type": "agent_message",
#                     "content": f"I encountered an error: {str(e)}"
#                 }
#         else:
#             # Handle informational requests
#             async for response in self._handle_informational_request(user_id, message):
#                 yield response
    
#     # async def _user_has_agent_wallet(self, user_id):
#     #     """Check if user has activated an agent wallet"""
#     #     wallet_info = await self.db_manager.get_agent_wallet(user_id)
#     #     return wallet_info is not None
    
#     # # Other methods (handling different intents, etc.)
    
#     async def _analyze_intent(self, message: str) -> Dict[str, Any]:
#         """
#         Analyze the user's message to determine intent using LLM
        
#         Returns:
#             Dict with 'type' (either 'action' or 'information'),
#             and if 'action', also includes 'action_name' and 'parameters'
#         """
#         # Get all available actions for context
#         action_descriptions = self.action_registry.get_action_descriptions()
        
#         # Create a system prompt for intent detection
#         system_prompt = f"""
#         You are an AI assistant that helps users manage their cryptocurrency portfolios.
#         Your task is to determine if the user's message contains an intent to execute a specific action.
        
#         Available actions:
#         {json.dumps(action_descriptions, indent=2)}
        
#         If the user's message indicates they want to execute one of these actions:
#         1. Return a JSON with the following structure:
#         {{
#             "type": "action",
#             "action_name": "<name of the action>",
#             "parameters": {{<required parameters for the action>}},
#             "description": "<brief description of what you understood>"
#         }}
        
#         If the user is asking for information or their message doesn't map to a specific action:
#         1. Return a JSON with the following structure:
#         {{
#             "type": "information",
#             "description": "<brief description of what the user is asking about>"
#         }}
        
#         Provide only the JSON response, nothing else.
#         """
        
#         # Get LLM response
#         response = await self.llm.ainvoke([
#             SystemMessage(content=system_prompt),
#             HumanMessage(content=message)
#         ])
        
#         # Parse the response
#         try:
#             intent_data = json.loads(response.content)
#             return intent_data
#         except Exception as e:
#             logger.error(f"Error parsing LLM response: {str(e)}")
#             # Default to information intent on parsing error
#             return {
#                 "type": "information",
#                 "description": "Unable to determine specific intent"
#             }
    
#     def _action_requires_wallet(self, action_name: str) -> bool:
#         """Check if an action requires a wallet"""
#         # Trade and rebalance actions require a wallet
#         wallet_required_actions = [
#             "execute_trade", 
#             "rebalance_portfolio"
#         ]
#         return action_name in wallet_required_actions
    
#     async def _user_has_agent_wallet(self, user_id: str) -> bool:
#         """Check if a user has a connected agent wallet"""
#         wallet = await self.db_manager.get_agent_wallet(user_id)
#         return wallet is not None and wallet.get("wallet_address") is not None
    
#     async def _handle_informational_request(self, user_id: str, message: str):
#         """Handle an informational request that doesn't map to a specific action"""
        
#         # Get user context
#         user_portfolio = await self.db_manager.get_user_portfolio(user_id)
#         has_wallet = await self._user_has_agent_wallet(user_id)
        
#         # Create context-aware prompt for answering questions
#         system_prompt = f"""
#         You are an AI portfolio manager assistant. You provide helpful information about cryptocurrency investing.
        
#         User has{'' if has_wallet else ' not'} connected a wallet.
        
#         User portfolio: {json.dumps(user_portfolio) if user_portfolio else 'No portfolio data available'}
        
#         Respond conversationally and helpfully. If you don't know something, say so.
#         If the user's request would be better handled by an action, suggest connecting a wallet (if needed)
#         and using commands like "Buy 0.1 ETH" or "Rebalance my portfolio".
#         """
        
#         # Get LLM response
#         response = await self.llm.ainvoke([
#             SystemMessage(content=system_prompt),
#             HumanMessage(content=message)
#         ])
        
#         # Yield response to user
#         yield {
#             "type": "agent_message",
#             "content": response.content
#         }
    
#     def _initialize_agent(self):
#         """Initialize the AgentKit React agent with necessary tools"""
#         # Initialize LLM
#         #llm = ChatOpenAI(model=self.config.get("model", "gpt-4o-mini"))
#         llm = self.llm
        
#         # Initialize AgentKit
#         agentkit = AgentKit(AgentKitConfig(
#             wallet_provider=self.wallet_provider,
#             action_providers=[
#                 erc20_action_provider(),  # ERC20 token actions
#                 pyth_action_provider(),   # Price feeds
#                 wallet_action_provider(), # Wallet operations
#                 weth_action_provider(),   # WETH-specific operations
#             ]
#         ))
        
#         # Get tools for LangChain integration
#         tools = get_langchain_tools(agentkit)
        
#         # Create agent configuration
#         agent_config = {"configurable": {"thread_id": "Portfolio Rebalancing Agent"}}
        
#         # Create and return the agent with tools
#         agent = create_react_agent(
#             llm,
#             tools=tools,
#             checkpointer=self.memory,
#             state_modifier=(
#                 "You are a helpful portfolio rebalancing agent that can interact onchain "
#                 "using blockchain wallets. You can analyze sentiment, perform statistical "
#                 "analysis, and execute trades to rebalance portfolios. Always be clear about "
#                 "fees and risks before executing trades."
#             ),
#         )
        
#         return agent, agent_config
    
#     #     # async def process_message(self, 
#     #     #                 user_id: str, 
#     #     #                 message: str, 
#     #     #                 conversation_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
#     #     # """
#     #     # Process a user message and return agent responses
    
#     # async def _execute_on_chain_action(self, user_id, message, intent):
#     #     """Handle execution of on-chain actions like trades"""

#     #             # Yields chunks of the response as they become available
#     #     # """
#     #     # try:
#     #     #     # Stream responses from the agent
#     #     #     async for chunk in self.agent.stream(
#     #     #         {"messages": [HumanMessage(content=message)]}, 
#     #     #         self.agent_config
#     #     #     ):
#     #     #         if "agent" in chunk:
#     #     #             yield {
#     #     #                 "type": "agent_response",
#     #     #                 "content": chunk["agent"]["messages"][0].content,
#     #     #                 "conversation_id": conversation_id
#     #     #             }
#     #     #         elif "tools" in chunk:
#     #     #             yield {
#     #     #                 "type": "tool_execution",
#     #     #                 "content": chunk["tools"]["messages"][0].content,
#     #     #                 "conversation_id": conversation_id
#     #     #             }
#     #     # except Exception as e:
#     #     #     logger.error(f"Error processing message: {str(e)}")
#     #     #     yield {
#     #     #         "type": "error",
#     #     #         "content": f"There was an error processing your request: {str(e)}",
#     #     #         "conversation_id": conversation_id
#     #     #     }
            
#     #     # Extract trade parameters from message using NLP
#     #     trade_params = await self._extract_trade_parameters(message)
        
#     #     # Call TradeAgent to execute the trade
#     #     result = await self.trade_agent.execute_trade(
#     #         user_id=user_id,
#     #         asset=trade_params['asset'],
#     #         amount=trade_params['amount'],
#     #         action=trade_params['action']
#     #     )
        
#     #     # Format response based on trade result
#     #     if result['success']:
#     #         yield {
#     #             "type": "agent_message",
#     #             "content": f"I've executed your trade: {result['message']}"
#     #         }
#     #         yield {
#     #             "type": "transaction_receipt",
#     #             "content": result
#     #         }
#     #     else:
#     #         yield {
#     #             "type": "agent_message",
#     #             "content": f"I encountered an issue: {result['message']}"
#     #         }
    
#     async def chat(self, 
#                   user_id: str, 
#                   message: str, 
#                   conversation_id: str = None) -> AsyncGenerator[str, None]:
#         """
#         Process a user message and return text responses
        
#         This is a simplified version of process_message that only yields
#         the text content of responses, for easier integration with the chat service.
        
#         Args:
#             user_id: User identifier
#             message: User message content
#             conversation_id: Optional conversation ID
            
#         Yields:
#             Text chunks of the response
#         """
#         async for response in self.process_message(user_id, message, conversation_id):
#             # Only yield the content, not the full response object
#             yield response["content"] 