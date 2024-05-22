# import logging
import os
import sys

from dotenv import load_dotenv
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

load_dotenv()
# logging.basicConfig(level=logging.DEBUG)

DATA_DIR = "data"
tokens_data_path = os.path.join(DATA_DIR, "tokens.json")
TELEGRAM_IP = "149.154.167.50"  # production
# TELEGRAM_IP = "149.154.167.40" # test
TELEGRAM_PORT = 80
TELEGRAM_DC_ID = 2


def get_session_id() -> None:
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if None in [api_id, api_hash]:
        raise ValueError("Must set env variables TELEGRAM_API_ID, TELEGRAM_API_HASH")

    with TelegramClient(StringSession(), api_id, api_hash) as client:
        client.session.set_dc(TELEGRAM_DC_ID, TELEGRAM_IP, TELEGRAM_PORT)
        session_str = client.session.save()
        print("Session created!", file=sys.stderr)
        print(
            "Add this to your .env file or otherwise pass via the environment to skip manual verification in future:",
            file=sys.stderr,
        )
        print(f"TELEGRAM_SESSION={session_str}", file=sys.stderr)


if __name__ == "__main__":
    get_session_id()
