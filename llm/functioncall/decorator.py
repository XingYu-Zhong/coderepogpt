import inspect
from typing import Callable, Dict, Any
registered_functions = []

def functioncall(description: str, param_descriptions: Dict[str, Dict[str, Any]] = None):
    if param_descriptions is None:
        param_descriptions = {}

    def decorator(func: Callable):
        params = inspect.signature(func).parameters
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        for name, param in params.items():
            if name == "self":
                continue
            param_info = param_descriptions.get(name, {})
            param_type = param_info.get("type", "string")
            param_desc = param_info.get("description", "")
            if param_type == "array":
                # 特别处理数组类型，包括items属性
                param_items = param_info.get("items", {})
                parameters["properties"][name] = {
                    "type": param_type,
                    "description": param_desc,
                    "items": param_items,  # 添加items属性
                }
            else:
                parameters["properties"][name] = {
                    "type": param_type,
                    "description": param_desc,
                }
            parameters["required"].append(name)

        registered_functions.append({
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description,
                "parameters": parameters,
            }
        })
        return func
    return decorator