import inspect
from typing import get_origin, get_args, Union

def get_openai_tools(tools_list: list) -> list[dict]:
    """
    Convert Python functions to OpenAI tool schema.
    Handles basic types and Optional hints.
    """
    openai_tools = []
    for func in tools_list:
        sig = inspect.signature(func)
        doc = func.__doc__ or ""
        
        params = {}
        required = []
        
        for name, param in sig.parameters.items():
            # Default type
            p_type = "string"
            
            # Handle types
            annotation = param.annotation
            origin = get_origin(annotation)
            args = get_args(annotation)
            
            # Check for Optional[Type] which is Union[Type, None]
            is_optional = False
            if origin is Union and type(None) in args:
                is_optional = True
                # Get the actual type
                types = [t for t in args if t is not type(None)]
                if types:
                    annotation = types[0]
            
            # Map basic types to JSON schema
            if annotation == int: 
                p_type = "integer"
            elif annotation == float: 
                p_type = "number"
            elif annotation == bool: 
                p_type = "boolean"
            elif annotation == dict: 
                p_type = "object"
            elif annotation == list: 
                p_type = "array"
            else:
                p_type = "string" # Default fallback
            
            params[name] = {
                "type": p_type,
                "description": f"Parameter {name}"
            }
            
            # Add to required if no default value 
            if param.default == inspect.Parameter.empty and not is_optional:
                required.append(name)
                
        tool_def = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": doc.strip(),
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": required
                }
            }
        }
        openai_tools.append(tool_def)
    return openai_tools
