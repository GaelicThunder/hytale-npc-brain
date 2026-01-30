import json
import logging
from openai import AsyncOpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, NPC_SYSTEM_PROMPT

# Configure logging
logger = logging.getLogger("NPC_Brain")

class NPCBrain:
    def __init__(self):
        """
        Initialize the LLM client (OpenAI compatible).
        """
        self.client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        # Initialize conversation history with the system prompt
        self.history = [{"role": "system", "content": NPC_SYSTEM_PROMPT}]

    async def think(self, user_name: str, message: str, game_context: dict) -> dict:
        """
        Process the game event and user message to generate a response/action.
        
        Args:
            user_name (str): The player's name.
            message (str): The chat message content.
            game_context (dict): Telemetry data (health, location, nearby mobs).
            
        Returns:
            dict: The action to be sent back to the game server.
        """
        # Formulate the context string
        context_str = f"Health: {game_context.get('health', 100)}% | Location: {game_context.get('pos', 'Unknown')} | Time: {game_context.get('time', 'Day')}"
        
        # Create the user prompt
        prompt = f"[{user_name}]: {message}\n[System Context]: {context_str}"
        self.history.append({"role": "user", "content": prompt})
        
        # Keep history manageable (last 10 turns)
        if len(self.history) > 12:
            self.history = [self.history[0]] + self.history[-10:]

        # Define the tools/functions the NPC can use
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
                                "enum": ["IDLE", "FOLLOW", "ATTACK", "GOTO", "INTERACT"],
                                "description": "The physical action to perform."
                            },
                            "target": {
                                "type": "string",
                                "description": "The target entity name or coordinates (e.g., 'Zombie', '100,64,100')."
                            },
                            "speech": {
                                "type": "string",
                                "description": "What the NPC says in chat."
                            }
                        },
                        "required": ["action_type", "speech"]
                    }
                }
            }
        ]

        try:
            # Call the LLM
            response = await self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=self.history,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "perform_action"}}
            )
            
            tool_call = response.choices[0].message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            
            # Log the thought process
            logger.info(f"Brain Decision: {function_args['action_type']} -> {function_args['speech']}")
            
            # Append assistant response to history
            self.history.append(response.choices[0].message)
            
            return function_args

        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return {
                "action_type": "IDLE",
                "speech": "I... I'm having a headache. (System Error)",
                "target": None
            }
