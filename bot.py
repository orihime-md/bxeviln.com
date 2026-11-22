"""DarkNet Photolab — a hacker-themed Telegram bot.

Features:
- Send any photo and pick from 8 Pillow-powered effects via caption buttons
- Hacker text tools: Base64, hex, binary, hashing, ROT13, Caesar, alias generator
- Matrix-styled command interface

Run: python bot.py
"""

import logging
import os
from io import BytesIO

import hashlib
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import cryptotools
from effects import EFFECT_NAMES, apply_effect, load_image, to_bytes
from keyboards import effects_menu, image_actions, tools_menu
from render import block

load_dotenv()

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

BANNER_TEXT = (
    "┌──────────────────────────────┐\n"
    "│  ▓▓ DARKNET PHOTOLAB v2.0 ▓▓ │\n"
    "└──────────────────────────────┘\n"
    "\n"
    "> CONNECTION ESTABLISHED... OK\n"
    "> ACCESS GRANTED. WELCOME,\n"
    "  OPERATIVE.\n"
    "\n"
    "SEND ME A PHOTO AND APPLY\n"
    "EFFECTS WITH BUTTONS. TAP\n"
    "TOOLS FOR TEXT UTILITIES."
)

def banner() -> str:
    return block(BANNER_TEXT)

HELP_TEXT = (
    "COMMAND LINE\n"
    "------------\n"
    "/start  establish connection\n"
    "/tools  text tool buttons\n"
    "/effects effect buttons\n"
    "\n"
    "TEXT TOOLS (command + text)\n"
    "---------------------------\n"
    "/encode  Base64 encode\n"
    "/decode  Base64 decode\n"
    "/hex     hex dump\n"
    "/unhex   hex to text\n"
    "/hash    SHA-256/SHA-1/MD5\n"
    "/binary  binary stream\n"
    "/rot13   ROT13 cipher\n"
    "/caesar  [n] Caesar cipher\n"
    "/alias   generate alias\n"
    "\n"
    "ALL TOOLS ARE FOR FUN AND\n"
    "LEARNING - PURELY SAFE."
)

WELCOME_NOTE = "TIP: effects are for your own photos — use them responsibly."

# ---------- command handlers ----------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        banner(), parse_mode="Markdown", reply_markup=image_actions()
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(block(HELP_TEXT), parse_mode="Markdown")

async def cmd_tools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        block("[ TOOL SELECT ]"), parse_mode="Markdown", reply_markup=tools_menu()
    )

async def cmd_effects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        block("[ EFFECT SELECT ]"), parse_mode="Markdown", reply_markup=effects_menu()
    )

def _tool_dispatch() -> dict:
    return {
        "encode": cryptotools.cmd_encode,
        "decode": cryptotools.cmd_decode,
        "hex": cryptotools.cmd_hex,
        "unhex": cryptotools.cmd_unhex,
        "hash": cryptotools.cmd_hash,
        "binary": cryptotools.cmd_binary,
        "rot13": cryptotools.cmd_rot13,
        "caesar": cryptotools.cmd_caesar,
        "alias": cryptotools.cmd_fakecredentials,
    }

def _make_text_command(func):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = " ".join(context.args) if context.args else ""
        try:
            await update.effective_message.reply_text(block(func(text)), parse_mode="Markdown")
        except cryptotools.ToolError as exc:
            await update.effective_message.reply_text(block(f"[ ERROR ] {exc}"), parse_mode="Markdown")
    return handler

# ---------- photo handling ----------

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.effective_message.photo[-1]
    file = await photo.get_file()
    buf = BytesIO()
    await file.download_to_memory(buf)
    context.user_data["photo_bytes"] = buf.getvalue()
    await update.effective_message.reply_text(
        block("> PHOTO INTERCEPTED.\n> CHOOSE YOUR WEAPON:"),
        parse_mode="Markdown",
        reply_markup=effects_menu(),
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "done":
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if data == "menu:effects":
        await query.edit_message_reply_markup(reply_markup=effects_menu())
        return

    if data.startswith("tool:imghash"):
        raw = context.user_data.get("photo_bytes")
        if not raw:
            await query.edit_message_text(block("[ ERROR ] NO PHOTO ON FILE."), parse_mode="Markdown")
            return
        digest = hashlib.sha256(raw).hexdigest()
        await query.edit_message_text(
            block(f"[ IMAGE FINGERPRINT ]\n\nSHA-256:\n{digest}"), parse_mode="Markdown"
        )
        return

    if data.startswith("effect:"):
        name = data.split(":", 1)[1]
        raw = context.user_data.get("photo_bytes")
        if not raw:
            await query.edit_message_text(block("[ ERROR ] NO PHOTO ON FILE."), parse_mode="Markdown")
            return
        await query.edit_message_text(
            block(f"> RUNNING {EFFECT_NAMES.get(name, name).upper()}\n> ROUTINE..."),
            parse_mode="Markdown",
        )
        try:
            img = load_image(raw)
            out = apply_effect(img, name)
            out_buf = to_bytes(out)
            caption = block(f"[ {EFFECT_NAMES.get(name, name).upper()} ]\nDARKNET PHOTOLAB")
            await query.message.reply_photo(photo=out_buf, caption=caption, parse_mode="Markdown")
            await query.edit_message_text(
                block("[ COMPLETE ] SEND ANOTHER\nPHOTO ANYTIME."), parse_mode="Markdown"
            )
        except Exception:
            await query.edit_message_text(
                block("[ ERROR ] EFFECT FAILED ON\nTHIS IMAGE. TRY A SMALLER\nPHOTO."),
                parse_mode="Markdown",
            )
        return

    if data.startswith("tool:"):
        name = data.split(":", 1)[1]
        usage = {
            "encode": "/encode Hello world",
            "decode": "/decode SGVsbG8=",
            "hex": "/hex Hello",
            "unhex": "/unhex 48 65 6c 6c 6f",
            "hash": "/hash Hello",
            "binary": "/binary Hi",
            "rot13": "/rot13 Hello",
            "caesar": "/caesar 5 Hello",
            "alias": "/alias nightowl",
        }.get(name, f"/{name} <text>")
        await query.edit_message_text(block(f"> SEND ME:\n{usage}"), parse_mode="Markdown")
        return

# ---------- entry point ----------

def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit(
            "BOT_TOKEN is not set. Create a bot with @BotFather on Telegram, "
            "copy the token, put it in your .env file as BOT_TOKEN=..., and run again."
        )

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("tools", cmd_tools))
    app.add_handler(CommandHandler("effects", cmd_effects))

    dispatch = _tool_dispatch()
    for name, func in dispatch.items():
        app.add_handler(CommandHandler(name, _make_text_command(func)))

    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("DarkNet Photolab online. Press Ctrl+C to disconnect.")
    app.run_polling()

if __name__ == "__main__":
    main()
