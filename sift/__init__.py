from __future__ import annotations

import os

from .client import Client
from .version import VERSION

__version__ = VERSION

api_key: str | None = os.environ.get("API_KEY")
account_id: str | None = os.environ.get("ACCOUNT_ID")
