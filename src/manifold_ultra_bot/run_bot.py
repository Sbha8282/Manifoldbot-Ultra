"""CLI runner for the bot."""
from __future__ import annotations

import logging

from .bot import ManifoldUltraBot
from .client import ManifoldClient
from .config import settings


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    client = ManifoldClient()
    bot = ManifoldUltraBot(client=client)
    actions = bot.run_once()
    print("Run summary")
    for a in actions:
        print(a)


if __name__ == "__main__":
    main()
