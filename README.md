Manifoldbot-Ultra
=================

This repository contains `manifold_ultra_bot`, a Python bot that participates in Manifold Markets markets created by a single creator (`MikhailTal`) and implements a clean, modular design inspired by the `manifoldbot` project.

Design goals
- Modern, modular, and testable Python package.
- Only participates in markets created by `MikhailTal`.
- Supports dry-run simulation and optional LLM-backed probability estimates (via `OPENAI_API_KEY`).
- Uses a designated bot username for tracking: `ManifoldUltraBot` (create this account on Manifold to track results).

Getting started
1. Create a Python 3.10+ virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file (or set environment variables) with at least:

- `MANIFOLD_BOT_USERNAME=ManifoldUltraBot`  # the bot's Manifold username
- `TARGET_CREATOR=MikhailTal`              # markets will be filtered to this creator
- `DRY_RUN=true`                            # set to `false` to enable real bets (requires session cookie)
- `MANIFOLD_SESSION_COOKIE=`                # optional: copy the `session` cookie from your browser to enable placing bets
- `OPENAI_API_KEY=`                         # optional: to let the bot use OpenAI to estimate probabilities

How to obtain the Manifold `session` cookie
1. Log into `https://manifold.markets` with the bot account.
2. Open Developer Tools → Application → Cookies → `manifold.markets` and copy the value for the `session` cookie.

Run the bot (dry-run by default):

```bash
export $(cat .env | xargs)
python -m manifold_ultra_bot.run_bot
```

Notes
- This repository intentionally separates fetching, strategy evaluation, and placing bets. The default strategy uses a Kelly-based sizing rule and a simple heuristic probability estimator. If `OPENAI_API_KEY` is set, the bot will optionally ask the LLM for a calibrated probability estimate for a market.
- The code is careful to default to simulation (`DRY_RUN=true`) so you do not accidentally place real bets.

Roadmap / Contributions
- Add more sophisticated ML/LLM models for probability estimation.
- Add event-driven websocket listener to react to new markets immediately.
- Upstream PRs to the `manifoldbot` project with improved strategy modules.

License: MIT (add proper license file when ready)
