from typing import Dict, Any, List
from pydantic import BaseModel

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, description: str, func, schema: Dict[str, Any]):
        self.tools[name] = {
            "description": description,
            "func": func,
            "parameters": schema
        }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": data["description"],
                "parameters": data["parameters"]
            }
            for name, data in self.tools.items()
        ]

# Define available tools
tools = ToolRegistry()

# Example Tool: Get Transits
tools.register_tool(
    name="get_current_transits",
    description="Fetches current planetary transits for the user's location to analyze immediate influences.",
    func=None, # Will map to AstrologyEngine.calculate_natal_chart with current date
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

# Example Tool: Get Dasha
tools.register_tool(
    name="get_dasha_periods",
    description="Fetches the current and upcoming Vimshottari Dasha periods for the user's natal chart.",
    func=None,
    schema={
        "type": "object",
        "properties": {
            "years_ahead": {"type": "integer", "description": "Number of years to look ahead."}
        },
        "required": ["years_ahead"]
    }
)

# Tool: Calculate Destiny Matrix
tools.register_tool(
    name="calculate_destiny_matrix",
    description="Calculates the 5 core nodes of the Destiny Matrix (Матрица Судьбы) based on the user's birth date to uncover their soul essence, past karma, and higher purpose.",
    func=None, # Maps to DestinyMatrixEngine
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

# Tool: Get Karma Timeline
tools.register_tool(
    name="get_karma_timeline",
    description="Calculates the deterministic timeline of major karmic events (transits + dasha hits) for the specified period.",
    func=None, # Maps to KarmaTimelineEngine
    schema={
        "type": "object",
        "properties": {
            "start_date": {"type": "string", "description": "ISO date string for start of timeline."},
            "end_date": {"type": "string", "description": "ISO date string for end of timeline."}
        },
        "required": ["start_date", "end_date"]
    }
)
