import zmq
import json
import logging
import signal
import sys
import time
from colorama import Fore, Style, init

# Import NPCBrain. Assuming llm_core.py exists and has think_sync or think method.
# If think is async, we might need to run a mini event loop or just run_until_complete.
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
        self.context = zmq.Context()
        self.socket = None
        self.running = True

    def run(self):
        """
        Main connection loop using ZMQ.
        Python acts as the SERVER (REP) listening for Game Events from Java (REQ).
        """
        logger.info(f"{Fore.CYAN}Starting Hytale NPC Brain (ZMQ Server)...{Style.RESET_ALL}")
        
        try:
            self.socket = self.context.socket(zmq.REP)
            self.socket.bind(f"tcp://*:5555")
            logger.info(f"{Fore.GREEN}Brain listening on tcp://*:5555{Style.RESET_ALL}")
        except zmq.ZMQError as e:
            logger.error(f"Could not bind ZMQ socket: {e}")
            return

        while self.running:
            try:
                # Wait for next request from client (Game Server)
                message = self.socket.recv_string()
                
                # Parse Message: "User|Message"
                parts = message.split("|", 2)
                
                response = "IDLE||"
                
                if len(parts) >= 2:
                    user = parts[0]
                    text = parts[1]
                    
                    logger.info(f"{Fore.YELLOW}[CHAT] {user}: {text}{Style.RESET_ALL}")
                    
                    # Think
                    # We wrap async call in sync since ZMQ loop is sync here
                    import asyncio
                    try:
                        decision = asyncio.run(self.brain.think(user, text, {}))
                    except:
                        # Fallback if think is not async or fails
                        decision = {"action_type": "CHAT", "speech": "Err... my brain hurts."}

                    # Format Response: "COMMAND|TARGET|CONTENT"
                    cmd = decision.get("action_type", "IDLE")
                    target = decision.get("target", "")
                    speech = decision.get("speech", "")
                    
                    response = f"{cmd}|{target}|{speech}"
                    logger.info(f"{Fore.BLUE}[DECISION] {response}{Style.RESET_ALL}")
                    
                else:
                    logger.debug(f"Received heartbeat/ping: {message}")

                # Send reply back to client
                self.socket.send_string(response)
                
            except Exception as e:
                logger.error(f"Error in Brain loop: {e}")
                # Try to recover socket state if possible, or restart loop
                try:
                    self.socket.send_string("ERROR||Brain Exception")
                except:
                    # If send fails, socket might be in bad state. Rebind?
                    pass

    def stop(self):
        self.running = False
        if self.context:
            self.context.term()

if __name__ == "__main__":
    bot = HytaleBot()
    
    def signal_handler(sig, frame):
        print(f"\n{Fore.RED}Shutting down...{Style.RESET_ALL}")
        bot.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    bot.run()
