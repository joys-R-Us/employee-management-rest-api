from __future__ import annotations

import os

from dotenv import load_dotenv


def load_env() -> None:
    """Load environment variables from a local .env file (if present).

    Call this once during application startup.
    """

    load_dotenv(override=False)

    # Optional: sanity defaults.
    os.environ.setdefault("ALGORITHM", "HS256")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

