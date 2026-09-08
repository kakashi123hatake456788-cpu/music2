"""
Run this ONCE, locally, to log in with the real account that will
join the voice chat and produce a session string.

    python generate_session.py

It will ask for the phone number, the login code sent to Telegram,
and (if enabled) your 2FA password. It then prints a SESSION_STRING
to paste into your .env file.

IMPORTANT: this string grants full access to that Telegram account.
Never share it, commit it to git, or paste it in a chat/bot log.
Use a secondary/alt account for this, not your main personal one,
and make sure this complies with Telegram's Terms of Service.
"""
from pyrogram import Client

API_ID = int(input("API_ID: ").strip())
API_HASH = input("API_HASH: ").strip()

with Client("session_gen", api_id=API_ID, api_hash=API_HASH, in_memory=True) as app:
    session_string = app.export_session_string()

print("\nYour SESSION_STRING (paste into .env):\n")
print(session_string)
