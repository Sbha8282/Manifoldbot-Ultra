"""Minimal Manifold client with fetch and place-bet (supporting dry-run)."""
from __future__ import annotations

import logging
from typing import Any

import requests

from .config import settings

logger = logging.getLogger(__name__)


class ManifoldClient:
    def __init__(self, base_url: str | None = None, session_cookie: str | None = None):
        self.base_url = base_url or settings.MANIFOLD_BASE_URL
        self.session_cookie = session_cookie or settings.MANIFOLD_SESSION_COOKIE
        self._session = requests.Session()
        if self.session_cookie:
            # Many users store the cookie named `session` from the browser
            self._session.headers.update({"Cookie": f"session={self.session_cookie}"})

    def fetch_markets_by_creator(self, creator: str, limit: int = 50) -> list[dict[str, Any]]:
        """Return raw market objects created by `creator`.

        This uses the public REST endpoint; field names are preserved from Manifold's public API.
        """
        url = f"{self.base_url}/api/v0/users/{creator}/markets?limit={limit}"
        logger.debug("Fetching markets for %s -> %s", creator, url)
        r = self._session.get(url, timeout=15)
        r.raise_for_status()
        return r.json()

    def place_bet(self, contract_id: str, amount: int, outcome: str | int, price: float | None = None) -> dict[str, Any]:
        """Place a bet. Requires a valid `session` cookie and DRY_RUN=False.

        The exact payload shape may change depending on Manifold internals; this implementation attempts
        a straightforward POST to `/api/v0/bets`.
        """
        if settings.DRY_RUN:
            logger.info("DRY RUN: would place bet on %s amount=%s outcome=%s price=%s", contract_id, amount, outcome, price)
            return {"simulated": True, "contractId": contract_id, "amount": amount, "outcome": outcome, "price": price}

        if not self.session_cookie:
            raise RuntimeError("No session cookie available for placing bets. Set MANIFOLD_SESSION_COOKIE or enable DRY_RUN for simulations.")

        payload: dict[str, Any] = {
            "contractId": contract_id,
            "amount": int(amount),
            "outcome": outcome,
        }
        if price is not None:
            payload["price"] = float(price)

        url = f"{self.base_url}/api/v0/bets"
        logger.debug("Placing bet payload=%s", payload)
        r = self._session.post(url, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
