"""Single async entrypoint for Claude Agent SDK query.

Each `run()` call is a fresh, stateless one-shot session. Wallclock is
enforced via asyncio.wait_for; turn cap is delegated to the SDK's
max_turns option. Tool dispatch is delegated to the in-process MCP
server passed in.
"""
from __future__ import annotations

import asyncio
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)

from mr.synth.limits import LimitExceeded


async def run(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    mcp_server: Any,
    allowed_tools: list[str],
    max_turns: int,
    wallclock_seconds: int,
) -> str:
    """Run a single, one-shot Claude Agent SDK query and return the final text."""
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        model=model,
        mcp_servers={"moat": mcp_server} if mcp_server is not None else {},
        allowed_tools=allowed_tools,
        max_turns=max_turns,
        permission_mode="bypassPermissions",
    )

    async def _collect() -> str:
        parts: list[str] = []
        async for message in query(prompt=user_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        parts.append(block.text)
                    else:
                        text = getattr(block, "text", None)
                        if text:
                            parts.append(text)
            else:
                # Tolerate test stand-ins that aren't AssistantMessage.
                content = getattr(message, "content", None)
                if content:
                    for block in content:
                        text = getattr(block, "text", None)
                        if text:
                            parts.append(text)
        return "".join(parts)

    try:
        return await asyncio.wait_for(_collect(), timeout=wallclock_seconds)
    except asyncio.TimeoutError as ex:
        raise LimitExceeded(
            f"wallclock cap exceeded: {wallclock_seconds}s"
        ) from ex
