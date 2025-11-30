"""Orchestration for running the Manifold participation bot."""
from __future__ import annotations

import logging
from typing import Any

from .client import ManifoldClient
from .config import settings
from .strategy import Strategy

logger = logging.getLogger(__name__)


class ManifoldUltraBot:
    def __init__(self, client: ManifoldClient | None = None, strategy: Strategy | None = None):
        self.client = client or ManifoldClient()
        self.strategy = strategy or Strategy()

    def run_once(self) -> list[dict[str, Any]]:
        """Fetch markets created by `TARGET_CREATOR`, evaluate, and (optionally) place bets.

        Returns a list of action summaries.
        """
        creator = settings.TARGET_CREATOR
        max_markets = settings.MAX_MARKETS_PER_RUN
        logger.info("Fetching up to %s markets by %s", max_markets, creator)
        markets = self.client.fetch_markets_by_creator(creator, limit=max_markets)
        actions: list[dict[str, Any]] = []
        for m in markets:
            try:
                decision = self.strategy.decide(m)
                if not decision["recommend"]:
                    logger.debug("No recommendation for market %s", m.get("id"))
                    continue

                # Determine stake amount. Here we use a very small fixed bankroll assumption for safety.
                bankroll = 1000  # play-money bankroll estimate; users should adapt this.
                fraction = decision["kelly_fraction"]
                stake = max(1, int(bankroll * fraction))

                # For binary markets, outcome 'YES' is typically represented; adapt if needed.
                outcome = "YES"
                res = self.client.place_bet(contract_id=m.get("id"), amount=stake, outcome=outcome, price=decision.get("market_price"))
                actions.append({"market_id": m.get("id"), "stake": stake, "decision": decision, "result": res})
            except Exception as e:
                logger.exception("Error handling market %s: %s", m.get("id"), e)
        return actions
