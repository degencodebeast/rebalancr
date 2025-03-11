# from typing import Dict, List, Type, Any, Callable, Awaitable
# import logging

# from .actions.base_action import BaseAction

# logger = logging.getLogger(__name__)

# class ActionRegistry:
#     """Registry of all available actions that can be executed"""
    
#     def __init__(self):
#         self.actions: Dict[str, BaseAction] = {}
    
#     def register_action(self, action: BaseAction) -> None:
#         """Register an action with the registry"""
#         action_name = action.get_name()
#         if action_name in self.actions:
#             logger.warning(f"Action {action_name} already registered. Overwriting.")
        
#         self.actions[action_name] = action
#         logger.info(f"Registered action: {action_name}")
    
#     def get_action(self, action_name: str) -> BaseAction:
#         """Get an action by name"""
#         if action_name not in self.actions:
#             raise ValueError(f"Action {action_name} not found in registry")
        
#         return self.actions[action_name]
    
#     def get_all_actions(self) -> List[BaseAction]:
#         """Get all registered actions"""
#         return list(self.actions.values())
    
#     def get_action_descriptions(self) -> Dict[str, Dict[str, Any]]:
#         """Get descriptions of all registered actions for LLM context"""
#         descriptions = {}
        
#         for name, action in self.actions.items():
#             descriptions[name] = {
#                 "description": action.get_description(),
#                 "parameters": action.get_parameters(),
#                 "signature": action.get_signature()
#             }
            
#         return descriptions 
