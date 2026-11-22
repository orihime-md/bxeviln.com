"""Render replies as edge-to-edge terminal-style message blocks.

Telegram sizes a message bubble to its widest line. Sending replies as
monospace code blocks padded to a fixed width makes every response occupy
the same full screen width, with no empty space on either side.
Tune WIDTH to make replies wider or narrower (36-44 works on phones).
"""

import textwrap

WIDTH = 38

def block(text: str, width: int = WIDTH) -> str:
    out = []
    for raw in text.split("\n"):
        if raw.strip():
            wrapped = textwrap.wrap(
                raw, width=width, break_long_words=True, break_on_hyphens=False
            )
            out.extend(wrapped or [""])
        else:
            out.append("")
    padded = [line.ljust(width) for line in out]
    return f"```\n" + "\n".join(padded) + "\n```"
