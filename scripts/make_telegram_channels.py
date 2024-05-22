import json
import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from telethon import password
from telethon.errors import SessionPasswordNeededError
from telethon.functions import account, channels, messages
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.types import Channel, InputChatUploadedPhoto

load_dotenv()
# logging.basicConfig(level=logging.DEBUG)

DATA_DIR = "data"
tokens_data_path = os.path.join(DATA_DIR, "tokens.json")
TELEGRAM_IP = "149.154.167.50" # production
# TELEGRAM_IP = "149.154.167.40" # test
TELEGRAM_PORT = 80
TELEGRAM_DC_ID = 2


def read_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(path: str, tokens: list[Any]) -> None:
    with open(path, "w", encoding="utf-8") as file:
        return json.dump(tokens, file, indent="\t")


def create_channel(client: TelegramClient, title: str, about: str) -> str:
    request = channels.CreateChannelRequest(title=title, about=about, broadcast=True)
    result = client(request)
    if not result.chats:
        raise TypeError("No chat found")

    new_channel = result.chats[0]
    if not isinstance(new_channel, Channel):
        raise TypeError("Chat is not a channel")

    channel = client.get_entity(new_channel)
    return channel


def set_channel_photo(client: TelegramClient, channel: Channel, ticker: str) -> None:
    filename = f"{ticker}.jpg"
    photo_path = os.path.join("pages", "static", filename)
    uploaded_file = client.upload_file(photo_path)
    request = channels.EditPhotoRequest(
        channel=channel, photo=InputChatUploadedPhoto(uploaded_file)
    )
    client(request)


def create_invite_link(client: TelegramClient, channel: Channel) -> str:
    request = messages.ExportChatInviteRequest(peer=channel)
    result = client(request)
    return result.link


# def transfer_ownership(
#     client: TelegramClient, channel: Channel, user: str, provided_password: str
# ) -> None:
#     try:
#         # Fetch the 2FA parameters
#         password_info = client(account.GetPasswordRequest())
#     except SessionPasswordNeededError:
#         print("2FA is not enabled on this account.")
#         return

#     checked_password = password.compute_check(password_info, provided_password)

#     request = channels.EditCreatorRequest(
#         channel=channel, user_id=user, password=checked_password
#     )
#     result = client(request)
#     print(result.stringify())


# def invite_user(client: TelegramClient, channel: Channel, user: str) -> None:
#     request = channels.InviteToChannelRequest(
#         channel=channel,
#         users=[user]
#     )
#     client(request)


# def make_admin(client: TelegramClient, channel: Channel, user: str) -> None:
#     client.edit_admin(channel, user, is_admin=True)


# def remove_admin(client: TelegramClient, channel: Channel, user: str) -> None:
#     client.edit_admin(channel, user, is_admin=False)


def create_channels() -> None:
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    # telegram_password = os.getenv("TELEGRAM_PASSWORD")
    session = os.getenv("TELEGRAM_SESSION")
    # if None in [api_id, api_hash, telegram_password]:
    if None in [api_id, api_hash]:
        raise ValueError(
            # "Must set env variables TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PASSWORD"
            "Must set env variables TELEGRAM_API_ID, TELEGRAM_API_HASH"
        )

    tokens = read_json_file(tokens_data_path)

    with TelegramClient(StringSession(session), api_id, api_hash) as client:
        if session is None:
            client.session.set_dc(TELEGRAM_DC_ID, TELEGRAM_IP, TELEGRAM_PORT)
            session_str = client.session.save()
            print("Session created!", file=sys.stderr)
            print(
                "Add this to your .env file or otherwise pass via the environment to skip manual verification in future:",
                file=sys.stderr,
            )
            print(f"TELEGRAM_SESSION={session_str}", file=sys.stderr)

        for token in tokens:
            if token.get("is_telegram_created"):
                print(f"Telegram channel exists, skipping: {token["ticker"]}")
                continue

            title = f"{token["name"]} (${token["ticker"]})"
            about = token["description"]
            # telegram_admin = token["telegram_admin"]

            channel = create_channel(client, title, about)
            set_channel_photo(client, channel, token["ticker"])

            invite_link = create_invite_link(client, channel)
            token["telegram_link"] = invite_link
            token["is_telegram_created"] = True

            print(f"Telegram channel for {token["ticker"]} created: {invite_link}")
            write_json_file(tokens_data_path, tokens)

            # transfer_ownership(client, channel, telegram_admin, telegram_password)



if __name__ == "__main__":
    create_channels()
