"""
jarvis/core/tools/tool_registry.py
Central registry of all pre-built tools with JSON Schema definitions.
Tools register themselves via @tool decorator. ReAct engine queries this
registry to know what tools are available.
"""

import inspect
import json
from typing import Callable, Dict, Any, Optional, List, get_type_hints
from dataclasses import dataclass, field
from functools import wraps


@dataclass
class ToolParam:
    name: str
    type: str           # "string", "integer", "boolean", "number"
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolDefinition:
    name: str
    description: str
    category: str       # "system", "network", "media", "file", "communication", "vision", "security"
    parameters: List[ToolParam] = field(default_factory=list)
    requires_permission: bool = False  # If True, NOVA asks user before executing
    fn: Callable = None

    def to_schema(self) -> dict:
        """Returns OpenAI-compatible function schema for LLM."""
        props = {}
        required = []
        for p in self.parameters:
            props[p.name] = {"type": p.type, "description": p.description}
            if p.required:
                required.append(p.name)
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required
            }
        }


class ToolRegistry:
    """Singleton registry of all available tools."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, ToolDefinition] = {}
        return cls._instance

    def register(self, tool_def: ToolDefinition):
        self._tools[tool_def.name] = tool_def
        print(f"[TOOLS] Registered: {tool_def.name} ({tool_def.category})")

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_all(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def get_schemas_for_llm(self) -> str:
        """Returns all tool schemas as a formatted string for the LLM prompt."""
        schemas = []
        for t in self._tools.values():
            schema = t.to_schema()
            schemas.append(schema)
        return json.dumps(schemas, indent=2)

    def execute(self, tool_name: str, **kwargs) -> str:
        t = self._tools.get(tool_name)
        if not t:
            return f"Error: Tool '{tool_name}' not found"
        try:
            # Filter kwargs to only accepted params
            sig = inspect.signature(t.fn)
            filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
            result = t.fn(**filtered)
            return str(result)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"


def tool(name: str, desc: str, category: str = "general", permission: bool = False):
    """Decorator to register a function as a NOVA tool."""
    def decorator(fn: Callable):
        # Auto-generate params from function signature
        sig = inspect.signature(fn)
        hints = get_type_hints(fn)
        params = []
        for param_name, param in sig.parameters.items():
            ptype = hints.get(param_name, str).__name__
            type_map = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}
            params.append(ToolParam(
                name=param_name,
                type=type_map.get(ptype, "string"),
                description=f"Parameter: {param_name}",
                required=param.default == inspect.Parameter.empty,
                default=None if param.default == inspect.Parameter.empty else param.default
            ))

        tool_def = ToolDefinition(
            name=name, description=desc, category=category,
            parameters=params, requires_permission=permission, fn=fn
        )
        ToolRegistry().register(tool_def)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator
