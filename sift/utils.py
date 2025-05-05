from __future__ import annotations

import json
import typing as t
import urllib.parse
from decimal import Decimal


def quote_path(s: str) -> str:
    # by default, urllib.quote doesn't escape forward slash; pass the
    # optional arg to override this
    return urllib.parse.quote(s, safe="")


class DecimalEncoder(json.JSONEncoder):
    def default(self, o: object) -> tuple[str] | t.Any:
        if isinstance(o, Decimal):
            return (str(o),)

        return super().default(o)
