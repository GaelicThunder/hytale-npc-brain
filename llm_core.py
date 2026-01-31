import json
import logging
from openai import AsyncOpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, NPC_SYSTEM_PROMPT

logger = logging.getLogger("NPC_Brain")

class NPCBrain:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        self.history = [{"role": "system", "content": NPC_SYSTEM_PROMPT}]

    async def think(self, user_name: str, message: str, game_context: dict) -> dict:
        # Context now includes nearby entities and visible blocks if available
        context_str = (
            f"Health: {game_context.get('health', 100)}% | "
            f"Location: {game_context.get('pos', 'Unknown')} | "
            f"Time: {game_context.get('time', 'Day')} | "
            f"Nearby: {game_context.get('nearby_entities', [])}"
        )
        
        prompt = f"[{user_name}]: {message}\n[System Context]: {context_str}"
        self.history.append({"role": "user", "content": prompt})
        
        if len(self.history) > 15:
            self.history = [self.history[0]] + self.history[-12:]

        # Expanded toolset for Mining and Combat
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "perform_action",
                    "description": "Decide on an action and speech for the NPC",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action_type": {
                                "type": "string", 
                                "enum": ["IDLE", "FOLLOW", "ATTACK", "GOTO", "INTERACT", "MINE", "FIND"],
                                "description": "The physical action. MINE=break block, FIND=search for object/mob."
                            },
                            "target": {
                                "type": "string",
                                "description": "Target name (e.g. 'Zombie', 'Copper Ore') or coords 'x,y,z'."
                            },
                            "speech": {
                                "type": "string",
                                "description": "What the NPC says."
                            }
                        },
                        "required": ["action_type", "speech"]
                    }
                }
            }
        ]

        try:
            response = await self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=self.history,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "perform_action"}}
            )
            
            tool_call = response.choices[0].message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"Brain Decision: {function_args['action_type']} -> {function_args['speech']}")
            self.history.append(response.choices[0].message)
            return function_args

        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return {"action_type": "IDLE", "speech": "Brain freeze...", "target": None}
