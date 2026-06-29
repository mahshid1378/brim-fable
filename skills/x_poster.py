"""speaks on x. wired up once the x developer account exists."""

import os

import tweepy
from dotenv import load_dotenv

load_dotenv()


def post(text: str) -> str:
    """post to x, return the tweet url."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    response = client.create_tweet(text=text)
    return f"https://x.com/i/status/{response.data['id']}"
