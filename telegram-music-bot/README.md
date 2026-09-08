# Telegram VC Music Bot

Streams audio into a Telegram group's voice chat. Uses two Telegram identities:

- **Bot** (via @BotFather) — handles user-facing commands (`/play`, `/skip`, ...).
- **Userbot** (a real Telegram account, via a session string) — actually joins
  the voice chat and streams audio, since bot accounts cannot join VCs directly.

Music is found and fetched with `yt-dlp`, and streamed with `pytgcalls`.

## Setup

1. **Install dependencies** (needs `ffmpeg` installed on your system too):
   ```
   pip install -r requirements.txt
   ```

2. **Get API credentials** from https://my.telegram.org (API_ID / API_HASH).

3. **Create a bot** with [@BotFather](https://t.me/BotFather) to get a `BOT_TOKEN`.

4. **Generate a userbot session string.** Use a secondary/alt Telegram account
   for this — not your main personal number — and read Telegram's Terms of
   Service on automation before running a userbot 24/7:
   ```
   python generate_session.py
   ```
   Follow the prompts (phone number, login code, 2FA if enabled). Copy the
   printed session string.

5. **Configure environment**: copy `.env.example` to `.env` and fill in
   `API_ID`, `API_HASH`, `BOT_TOKEN`, and `SESSION_STRING`.

6. **Add both accounts to your group**:
   - Add the bot and give it permission to send messages / manage voice chats.
   - Add the userbot account as a regular member, and make sure a voice chat
     is already started in the group (the userbot joins an existing VC; it
     doesn't currently start one for you).

7. **Run it**:
   ```
   python bot.py
   ```

## Commands (used in the group, sent to the bot)

- `/play <song name or URL>` — search YouTube (or use a direct link) and
  play/queue it.
- `/pause` / `/resume`
- `/skip` — skip to the next queued track.
- `/queue` — show what's playing and what's queued.
- `/stop` — clear the queue and leave the voice chat.

## Notes & things to adapt

- This scaffold downloads full tracks before playing (simple and reliable).
  For lower latency you can stream directly from a resolved URL instead of
  downloading first — `pytgcalls`' `MediaStream` accepts a direct media URL.
- Only one track plays at a time per chat; queueing is per-chat via an
  in-memory dict, so it resets if the process restarts. Swap in Redis/SQLite
  if you need persistence across restarts.
- `ALLOWED_CHATS` in `.env` lets you restrict which groups the bot responds
  in; leave blank to allow any group it's added to.
- Keep the `SESSION_STRING` secret — it's equivalent to full login access to
  that Telegram account.
- Downloaded files pile up in `downloads/`; add a cleanup step (e.g. delete
  after playback) if you're running this long-term.
