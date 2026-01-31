import asyncio
import websockets
import json
import logging
import signal
import sys
from colorama import Fore, Style, init

from config import SERVER_IP, SERVER_PORT, WS_PATH
from llm_core import NPCBrain

# Initialize Colorama
init()

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("HytaleNPC")

class HytaleBot:
    def __init__(self):
        self.brain = NPCBrain()
        self.uri = f"ws://{SERVER_IP}:{SERVER_PORT}{WS_PATH}"
        self.running = True

    async def connect(self):
        """
        Main connection loop.
        """
        logger.info(f"{Fore.CYAN}Starting Hytale NPC Brain...{Style.RESET_ALL}")
        
        while self.running:
            try:
                logger.info(f"Connecting to {self.uri}...")
                async with websockets.connect(self.uri) as websocket:
                    logger.info(f"{Fore.GREEN}Connected to Game Server!{Style.RESET_ALL}")
                    
                    # Login handshake (if required by your custom server impl)
                    # await websocket.send(json.dumps({"type": "auth", "token": "npc_token"}))

                    async for message in websocket:
                        await self.handle_message(websocket, message)
                        
            except ConnectionRefusedError:
                logger.error(f"{Fore.RED}Connection refused. Is the Hytale Server running? Retrying in 5s...{Style.RESET_ALL}")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error: {e}")
                await asyncio.sleep(5)

    async def handle_message(self, ws, message):
        """
        Handle incoming WebSocket messages from the game.
        """
        try:
            data = json.loads(message)
            event_type = data.get("type")
            
            # Log raw event (debug)
            # logger.debug(f"Event: {data}")

            if event_type == "chat":
                # Player spoke in chat
                user = data.get("sender", "Unknown")
                text = data.get("message", "")
                
                # Ignore self
                if user == "Gillian":
                    return

                logger.info(f"{Fore.YELLOW}[CHAT] {user}: {text}{Style.RESET_ALL}")
                
                # Context (Mocking if missing from packet)
                ctx = data.get("context", {"health": 100, "pos": "0,0,0", "time": "Day"})
                
                # Process with Brain
                decision = await self.brain.think(user, text, ctx)
                
                # Send Action back to Server
                response = {
                    "type": "npc_command",
                    "command": decision["action_type"],
                    "target": decision.get("target"),
                    "chat": decision["speech"]
                }
                
                await ws.send(json.dumps(response))
                logger.info(f"{Fore.BLUE}[ACTION] Sent: {response}{Style.RESET_ALL}")

            elif event_type == "tick":
                # Periodic updates (optional AI processing)
                pass

        except json.JSONDecodeError:
            logger.error("Received invalid JSON")

    def stop(self):
        self.running = False

async def main():
    bot = HytaleBot()
    
    # Graceful shutdown
    def signal_handler(sig, frame):
        print(f"\n{Fore.RED}Shutting down...{Style.RESET_ALL}")
        bot.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    await bot.connect()

if __name__ == "__main__":
    asyncio.run(main())
