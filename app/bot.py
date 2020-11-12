import os
from typing import List

from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter

from app.youtrack import get_previews


app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)

slack_web_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def send_message(channel: str, ts, previews: List[str]):
    if previews:
        slack_web_client.chat_postMessage(**get_message_payload(channel, ts, previews))


def get_message_payload(channel: str, ts, previews: List[str]) -> dict:
    return {
        "channel": channel,
        "thread_ts": ts,
        "username": os.environ["BOT_USERNAME"],
        "blocks": get_divided_blocks(previews),
        "mrkdwn": "true",
    }


def get_divided_blocks(previews: List[str]) -> List[dict]:
    blocks = [get_message_block(previews.pop(0))]
    for preview in previews:
        blocks.extend([{"type": "divider"}, get_message_block(preview)])
    return blocks


def get_message_block(text: str) -> dict:
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text,
        },
    }


@slack_events_adapter.on("message")
def handle_youtrack_urls(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")

    if user_id != os.environ["BOT_ID"]:
        text = event.get("text")
        ts = event.get("ts")
        if "youtrack" in text and "issue" in text:
            send_message(channel_id, ts, [preview for preview in get_previews(text) if preview])


if __name__ == "__main__":
    app.run(port=3000)
