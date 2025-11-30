"""Strategy module: estimate probabilities and compute Kelly stake."""
from __future__ import annotations

import math
import logging
import os
from typing import Any

import requests

from .config import settings

logger = logging.getLogger(__name__)


def kelly_fraction(p: float, price: float) -> float:
    """Compute Kelly fraction for a binary market.

    `p` is our estimated probability of the YES outcome. `price` is the market's current probability price
    (0..1) for the YES outcome. The fair odds b = price/(1-price). Kelly fraction f = (p*(b+1)-1)/b.
    Clip to 0..1.
    """
    if price <= 0 or price >= 1:
        return 0.0
    b = price / (1 - price)
    f = (p * (b + 1) - 1) / b
    f = max(0.0, min(1.0, f))
    return f


class Strategy:
    def __init__(self, openai_key: str | None = None):
        self.openai_key = openai_key or settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    def _estimate_with_openai(self, prompt: str) -> float | None:
        if not self.openai_key:
            return None
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a probability estimator. Return a single number between 0 and 1 indicating probability of YES."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.0,
            }
            r = requests.post(url, json=data, headers=headers, timeout=15)
            r.raise_for_status()
            out = r.json()
            text = out["choices"][0]["message"]["content"].strip()
            # Try to extract a number
            import re

            m = re.search(r"([0-9]*\.?[0-9]+)", text)
            if m:
                val = float(m.group(1))
                if 0.0 <= val <= 1.0:
                    return val
        except Exception as e:  # pragma: no cover - optional runtime behavior
            logger.warning("OpenAI estimation failed: %s", e)
        return None

    def estimate_probability(self, market: dict[str, Any]) -> float:
        """Estimate the probability of the YES outcome for a binary market.

        Strategy:
        - If `openai` is configured, ask the LLM to estimate probability (preferred).
        - Otherwise, use a heuristic based on title/description.
        """
        text = (market.get("question") or market.get("slug") or "").strip()
        prompt = f"Return probability (0..1) that the following statement is true: {text}"
        p = self._estimate_with_openai(prompt)
        if p is not None:
            logger.info("OpenAI estimated p=%.3f for market %s", p, market.get("id"))
            return p

        # Heuristic fallback: look for strong directional words
        q = text.lower()
        if any(w in q for w in ["will", "win", "beats", "over", "under"]):
            base = 0.45
        else:
            base = 0.5
        # Slight adjustment based on length/complexity
        if len(q) < 40:
            base += 0.02
        p = max(0.01, min(0.99, base))
        logger.debug("Heuristic estimated p=%.3f for market %s", p, market.get("id"))
        return p

    def decide(self, market: dict[str, Any]) -> dict[str, Any]:
        """Given a market, return a decision dict with recommended stake fraction and estimated p.

        The returned dict has keys: `probability`, `market_price`, `kelly_fraction`, `recommend` (bool).
        """
        # Market shape may contain `probability` or `probability` nested
        price = None
        if market.get("probability") is not None:
            price = float(market["probability"])
        elif isinstance(market.get("mechanism"), str) and market.get("mechanism") == "binary":
            # some endpoints include `pool`/`probability` fields differently; default to 0.5
            price = float(market.get("probability") or 0.5)
        else:
            price = float(market.get("probability") or 0.5)

        p = float(self.estimate_probability(market))
        k = kelly_fraction(p, price)
        recommend = k > 0.01  # threshold
        result = {
            "probability": p,
            "market_price": price,
            "kelly_fraction": k,
            "recommend": recommend,
        }
        logger.debug("Decision for market %s -> %s", market.get("id"), result)
        return result
