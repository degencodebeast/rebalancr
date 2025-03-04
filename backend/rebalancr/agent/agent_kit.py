from typing import List, Dict, Any, Optional
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from ..execution.action_provider import ActionProvider, Action
from ..intelligence.agent_kit.wallet_provider import WalletProvider
from ..intelligence.allora.client import AlloraClient
from ..intelligence.market_analysis import MarketAnalyzer
from ..intelligence.intelligence_engine import IntelligenceEngine
from ..execution.action_provider import TradeActionProvider
#from ..execution.action_provider import AnalysisActionProvider

logger = logging.getLogger(__name__)

class AgentKit:
    """
    Core class that manages action providers and agent execution
    """
    def __init__(self, 
                 action_providers: List[ActionProvider],
                 wallet_provider: Optional[WalletProvider] = None,
                 llm_model: str = "gpt-4o"):
        self.action_providers = action_providers
        self.wallet_provider = wallet_provider
        self.actions = self._collect_actions()
        
        # Initialize LLM
        self.llm = ChatOpenAI(model=llm_model, temperature=0)
        
        # Create tools from actions
        self.tools = self._create_tools()
        
        # Create memory for conversation history
        self.memory = MemorySaver()
        
        # Create agent with ReAct pattern
        self.agent, self.agent_config = self._create_agent()
    
    def _collect_actions(self) -> Dict[str, Action]:
        """Collect all actions from providers into a single map"""
        actions = {}
        
        for provider in self.action_providers:
            for action in provider.get_actions():
                if action.name in actions:
                    logger.warning(f"Action {action.name} already registered. Overwriting.")
                
                actions[action.name] = action
                logger.info(f"Registered action: {action.name}")
        
        return actions
    
    def _create_tools(self) -> List[Tool]:
        """Convert actions to LangChain tools"""
        tools = []
        
        for name, action in self.actions.items():
            tools.append(
                Tool(
                    name=name,
                    description=action.description,
                    func=lambda action_name=name, **kwargs: self._execute_action(action_name, **kwargs)
                )
            )
        
        return tool
    
    async def _execute_action(self, action_name: str, **kwargs) -> str:
        """Execute an action and return a string result for the agent"""
        try:
            if action_name not in self.actions:
                return f"Error: Action '{action_name}' not found"
            
            action = self.actions[action_name]
            
            # Execute the action
            result = await action.execute(**kwargs)
            
            # Convert result to string for agent
            return f"Action executed: {action_name}\nResult: {result}"
        except Exception as e:
            logger.error(f"Error executing action {action_name}: {str(e)}")
            return f"Error executing action {action_name}: {str(e)}"
    
    def _create_agent(self):
        """Create a ReAct agent with tools"""
        agent_instructions = f"""
        You are a portfolio management agent that can execute various actions.
        
        Available actions:
        {', '.join(self.actions.keys())}
        
        Before executing actions that involve trading or portfolio changes, you should:
        1. Check if the user has connected a wallet
        2. Explain what you're about to do
        3. Ask for confirmation if it involves financial transactions
        
        For informational requests, respond directly without using tools.
        For action requests, use the appropriate tool with the required parameters.
        """
        
        # Create agent with ReAct pattern
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            checkpointer=self.memory,
            state_modifier=agent_instructions
        )
        
        # Create default config
        config = {"configurable": {"thread_id": "Rebalancr Portfolio Agent"}}
        
        return agent, config
    
    async def process_message(self, user_id: str, message: str):
        """Process a user message and return streaming results"""
        # Add user_id to all tool parameters
        augmented_tools = []
        for tool in self.tools:
            # Create a wrapped function that includes user_id
            async def wrapped_func(*args, tool=tool, **kwargs):
                kwargs["user_id"] = user_id
                return await tool.func(**kwargs)
            
            # Create a new tool with the wrapped function
            augmented_tools.append(
                Tool(
                    name=tool.name,
                    description=tool.description,
                    func=wrapped_func
                )
            )
        
        # Create stream results
        messages = [HumanMessage(content=message)]
        stream = await self.agent.stream({"messages": messages}, self.agent_config)
        
        # Yield streaming results
        async for chunk in stream:
            if "agent" in chunk:
                yield {
                    "type": "agent_message",
                    "content": chunk["agent"]["messages"][0].content
                }
            elif "tools" in chunk:
                yield {
                    "type": "tool_execution",
                    "content": chunk["tools"]["messages"][0].content
                }

class RebalancerAgentKit(AgentKit):
    """
    Domain-specific extension of AgentKit for portfolio rebalancing
    with market intelligence capabilities.
    """
    def __init__(self, 
                 action_providers,
                 wallet_provider=None,
                 llm_model="gpt-4o",
                 config=None):
        # Initialize base AgentKit
        super().__init__(action_providers, wallet_provider, llm_model)
        
        # Initialize domain-specific components
        if config:
            self.allora_client = AlloraClient(api_key=config.ALLORA_API_KEY)
            self.market_analyzer = MarketAnalyzer()
            self.intelligence_engine = IntelligenceEngine(
                allora_client=self.allora_client,
                market_analyzer=self.market_analyzer,
                config=config
            )
        
    @classmethod
    def create_with_default_providers(cls, config, wallet_provider=None):
        """Factory method to create RebalancerAgentKit with default providers"""
        # Create necessary components
        allora_client = AlloraClient(api_key=config.ALLORA_API_KEY)
        market_analyzer = MarketAnalyzer()
        intelligence_engine = IntelligenceEngine(
            allora_client=allora_client,
            market_analyzer=market_analyzer,
            config=config
        )
        
        # Create providers
        action_providers = [
            TradeActionProvider(
                trade_agent=intelligence_engine,
                wallet_provider=wallet_provider,
                market_analyzer=market_analyzer
            ),
            # AnalysisActionProvider(
            #     intelligence_engine=intelligence_engine,
            #     market_analyzer=market_analyzer
            # )
            # Add other providers as needed
        ]
        
        # Create and return the RebalancerAgentKit instance
        return cls(
            action_providers=action_providers,
            wallet_provider=wallet_provider,
            config=config
        ) 