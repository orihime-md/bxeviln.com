"""Inline keyboard layouts with hacker-style caption buttons."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

EFFECT_BUTTONS = [
    ("glitch", "⚡ Glitch"),
    ("matrix", "🌱 Matrix Rain"),
    ("terminal", "🖥 Terminal"),
    ("cyber", "🌆 Cyber Punk"),
    ("vhs", "📼 VHS Tape"),
    ("deepfry", "🔥 Deep Fry"),
    ("invert", "🌓 Invert"),
    ("encrypt", "🔒 Encrypt Slices"),
]

TOOL_BUTTONS = [
    ("encode", "🔐 Encode B64"),
    ("decode", "🔓 Decode B64"),
    ("hex", "🧪 Hex"),
    ("unhex", "🧫 Un-Hex"),
    ("hash", "#️⃣ Hash"),
    ("binary", "💾 Binary"),
    ("rot13", "🔤 ROT13"),
    ("caesar", "🏛 Caesar"),
    ("alias", "🕵 Generate Alias"),
]

def _pair(buttons: list) -> list:
    return [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

def effects_menu() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(label, callback_data=f"effect:{name}") for name, label in EFFECT_BUTTONS]
    return InlineKeyboardMarkup(_pair(buttons) + [[InlineKeyboardButton("✅ Done", callback_data="done")]])

def tools_menu() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(label, callback_data=f"tool:{name}") for name, label in TOOL_BUTTONS]
    return InlineKeyboardMarkup(_pair(buttons))

def image_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 Apply Effect", callback_data="menu:effects")],
        [InlineKeyboardButton("📊 Image Hash", callback_data="tool:imghash")],
        [InlineKeyboardButton("🗑 Remove", callback_data="done")],
    ])
