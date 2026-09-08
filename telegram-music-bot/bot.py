import asyncio
import os

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, Update
from pytgcalls.types.stream import StreamEnded

from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, ALLOWED_CHATS
from music import downloader, queue_manager

# The BOT: what users type commands to (/play, /skip, ...)
bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# The USERBOT: a real account session that actually joins the voice chat
userbot = Client("music_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# PyTgCalls wraps the userbot client to stream audio into the VC
call_py = PyTgCalls(userbot)


def allowed(chat_id: int) -> bool:
    return ALLOWED_CHATS is None or chat_id in ALLOWED_CHATS


async def play_next(chat_id: int):
    track = queue_manager.pop_next(chat_id)
    if track is None:
        queue_manager.set_now_playing(chat_id, None)
        await call_py.leave_call(chat_id)
        return
    if track.filepath is None:
        track = await downloader.download(track)
    queue_manager.set_now_playing(chat_id, track)
    await call_py.play(chat_id, MediaStream(track.filepath))


@bot.on_message(filters.command("play") & filters.group)
async def play_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if not allowed(chat_id):
        return
    if len(message.command) < 2:
        await message.reply("Usage: /play <song name or link>")
        return

    query = message.text.split(None, 1)[1]
    status = await message.reply(f"🔎 Searching: {query}")

    try:
        track = await downloader.search(query)
    except Exception as e:
        await status.edit(f"❌ Couldn't find that: {e}")
        return

    now_playing = queue_manager.get_now_playing(chat_id)
    queue_manager.push(chat_id, track)

    if now_playing is None:
        track = queue_manager.pop_next(chat_id)
        track = await downloader.download(track)
        queue_manager.set_now_playing(chat_id, track)
        try:
            await call_py.play(chat_id, MediaStream(track.filepath))
        except Exception:
            # not yet in the call -> join it with this stream
            await call_py.play(chat_id, MediaStream(track.filepath))
        await status.edit(f"▶️ Now playing: {track.title}")
    else:
        await status.edit(f"➕ Queued: {track.title}")


@bot.on_message(filters.command("skip") & filters.group)
async def skip_cmd(client: Client, message: Message):
    if not allowed(message.chat.id):
        return
    await play_next(message.chat.id)
    await message.reply("⏭ Skipped.")


@bot.on_message(filters.command("stop") & filters.group)
async def stop_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if not allowed(chat_id):
        return
    queue_manager.clear(chat_id)
    await call_py.leave_call(chat_id)
    await message.reply("⏹ Stopped and left the voice chat.")


@bot.on_message(filters.command("pause") & filters.group)
async def pause_cmd(client: Client, message: Message):
    if not allowed(message.chat.id):
        return
    await call_py.pause_stream(message.chat.id)
    await message.reply("⏸ Paused.")


@bot.on_message(filters.command("resume") & filters.group)
async def resume_cmd(client: Client, message: Message):
    if not allowed(message.chat.id):
        return
    await call_py.resume_stream(message.chat.id)
    await message.reply("▶️ Resumed.")


@bot.on_message(filters.command("queue") & filters.group)
async def queue_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if not allowed(chat_id):
        return
    now = queue_manager.get_now_playing(chat_id)
    q = queue_manager.peek_queue(chat_id)
    lines = []
    if now:
        lines.append(f"▶️ Now playing: {now.title}")
    if q:
        lines.append("\nUp next:")
        lines += [f"{i+1}. {t.title}" for i, t in enumerate(q)]
    await message.reply("\n".join(lines) if lines else "Queue is empty.")


@call_py.on_update()
async def on_stream_end(client: PyTgCalls, update: Update):
    if isinstance(update, StreamEnded):
        await play_next(update.chat_id)


async def main():
    await bot.start()
    await userbot.start()
    await call_py.start()
    print("Bot, userbot, and call client all started. Listening for commands...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
