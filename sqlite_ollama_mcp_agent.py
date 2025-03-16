import json
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, List
import asyncio

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL_NAME = "llama3"  # or any other model you have pulled in Ollama

# System prompt remains similar but slightly modified for Ollama
SYSTEM_PROMPT = """You are a helpful assistant capable of accessing external functions and engaging in casual chat. Use the responses from these function calls to provide accurate and informative answers. The answers should be natural and hide the fact that you are using tools to access real-time information. Guide the user about available tools and their capabilities. Always utilize tools to access real-time information when required. Engage in a friendly manner to enhance the chat experience.

# Tools

{tools}

# Notes 

- Ensure responses are based on the latest information available from function calls.
- Maintain an engaging, supportive, and friendly tone throughout the dialogue.
- Always highlight the potential of available tools to assist users comprehensively."""

# Initialize OpenAI client with Ollama API
client = AsyncOpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="not-needed"  # Ollama doesn't require an API key
)

# ... rest of the MCPClient class remains the same ...

async def agent_loop(query: str, tools: dict, messages: List[dict] = None):
    """
    Main interaction loop that processes user queries using Ollama and available tools.
    """
    messages = (
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    tools="\n- ".join(
                        [
                            f"{t['name']}: {t['schema']['function']['description']}"
                            for t in tools.values()
                        ]
                    )
                ),
            },
        ]
        if messages is None
        else messages
    )
    messages.append({"role": "user", "content": query})

    # Query Ollama with the system prompt, user query, and available tools
    first_response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=([t["schema"] for t in tools.values()] if len(tools) > 0 else None),
        temperature=0,
    )

    # ... rest of the agent_loop function remains the same ...