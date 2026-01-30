# Hytale NPC Companion (LLM Powered)

This project implements an AI-powered NPC companion for a Hytale private server (e.g., Sanasol based or custom implementations).

It uses **OpenAI** (or local LLMs like Ollama) to generate realistic dialogue and decisions.

## Architecture

1.  **Hytale Server**: Runs the game (Java/C#). It must expose a WebSocket interface or listen for bot connections.
2.  **NPC Brain (This Repo)**: A Python script that connects to the server via WebSocket, listens for events (Chat, Damage, etc.), and sends back commands.

## Prerequisites

- Python 3.10+
- An OpenAI API Key (or a running local LLM)
- A Hytale Server configured to accept WebSocket connections (see `integration` notes).

## Setup

1.  Clone this repo:
    ```bash
    git clone https://github.com/GaelicThunder/hytale-npc-brain.git
    cd hytale-npc-brain
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure `.env`:
    Copy `.env.example` to `.env` and fill in your details:
    ```ini
    SERVER_IP=127.0.0.1
    SERVER_PORT=8080
    LLM_API_KEY=sk-proj-xxxx
    ```

## Usage

Start the brain:
```bash
python main.py
```

The bot will attempt to connect to `ws://SERVER_IP:SERVER_PORT/`.

## Integration with Hytale Server

Since Hytale server APIs vary (leaked/custom), this bot expects a JSON WebSocket protocol. You may need to adapt your server plugin to match this schema:

**Incoming to Python (from Game):**
```json
{
  "type": "chat",
  "sender": "Gaël",
  "message": "Come here!",
  "context": {
    "health": 100,
    "pos": "120, 65, -40"
  }
}
```

**Outgoing to Game (from Python):**
```json
{
  "type": "npc_command",
  "command": "FOLLOW",
  "target": "Gaël",
  "chat": "On my way, chief!"
}
```
