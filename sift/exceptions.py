from __future__ import annotations

import typing as t


class ApiException(Exception):
    def __init__(
        self,
        message: str,
        url: str,
        http_status_code: int | None = None,
        body: dict[str, t.Any] | None = None,
        api_status: int | None = None,
        api_error_message: str | None = None,
        request: dict[str, t.Any] | None = None,
    ) -> None:
        Exception.__init__(self, message)

        self.url = url
        self.http_status_code = http_status_code
        self.body = body
        self.api_status = api_status
        self.api_error_message = api_error_message
        self.request = request
