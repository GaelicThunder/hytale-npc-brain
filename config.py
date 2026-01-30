import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================================
# SERVER CONFIGURATION
# ==========================================
# The IP address of the Hytale Server (or the bridge plugin)
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
# The WebSocket port exposed by the server for NPC control
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))
# WebSocket URI path (if needed)
WS_PATH = os.getenv("WS_PATH", "/")

# ==========================================
# LLM CONFIGURATION
# ==========================================
# API Key for OpenAI or local provider (e.g. Ollama)
LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-proj-placeholder")
# Model name (e.g., 'gpt-4o', 'gpt-3.5-turbo', 'llama3')
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
# Base URL (change this if using Ollama locally, e.g., 'http://localhost:11434/v1')
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

# ==========================================
# NPC CONFIGURATION
# ==========================================
NPC_NAME = "Gillian"
# The system prompt defining the NPC's behavior
NPC_SYSTEM_PROMPT = """You are Gillian, a helpful and intelligent NPC companion in the world of Hytale.
You are assisting a player named Gaël.
You are an expert in survival, combat, and exploration.
Your tone is friendly, slightly geeky, but professional when danger is near.
You act based on the user's commands but also have your own preservation instinct.
When you respond, you must choose an action (MOVE, ATTACK, FOLLOW, WAIT) and a spoken phrase.
"""
