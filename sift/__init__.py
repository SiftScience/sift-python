from __future__ import annotations

from .client import Client
from .version import VERSION

__version__ = VERSION

api_key: str | None = None
account_id: str | None = None
