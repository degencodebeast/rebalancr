import sys
import time
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from rebalancr.intelligence.agent_kit.service import AgentKitService
from rebalancr.config import Settings  # Your app configuration

def initialize_agent(config: Settings):
    """Initialize the agent with the consolidated AgentKitService."""
    service = AgentKitService.get_instance(config)
    memory = MemorySaver()
    config_dict = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}
    
    # Create a ReAct agent using the LLM and tools from the service.
    agent_executor = create_react_agent(
        service.llm,
        tools=service.tools,
        checkpointer=memory,
        state_modifier=(
            "You are a helpful financial agent that can perform on-chain transactions "
            "like depositing funds and rebalancing portfolios. Before executing actions, "
            "verify wallet details and explain your steps. If a 5XX error occurs, ask the user "
            "to try again later."
        ),
    )
    return agent_executor, config_dict

def run_autonomous_mode(agent_executor, config, interval=10):
    print("Starting autonomous mode...")
    while True:
        try:
            thought = (
                "Be creative and perform an on-chain action to help the user."
            )
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)

def run_chat_mode(agent_executor, config):
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")
        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)

def choose_mode():
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")
        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")

def main():
    print("Starting Agent...")
    settings = Settings()  # Load your configuration settings (from .env or similar)
    agent_executor, config = initialize_agent(settings)
    mode = choose_mode()
    if mode == "chat":
        run_chat_mode(agent_executor, config)
    elif mode == "auto":
        run_autonomous_mode(agent_executor, config)

if __name__ == "__main__":
    main() 