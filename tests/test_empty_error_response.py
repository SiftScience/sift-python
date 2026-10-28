from __future__ import annotations

from unittest import TestCase, mock

import requests

from sift.client import Client, Response
from sift.exceptions import ApiException


class TestEmptyErrorResponse(TestCase):
    def test_empty_and_whitespace_errors_raise(self) -> None:
        for status in (400, 401, 429, 500, 503):
            for body in (b"", b" "):
                with self.subTest(status=status, body=body):
                    response = requests.Response()
                    response.status_code = status
                    response.url = "https://api.sift.com/v205/events"
                    response._content = body
                    with self.assertRaises(ApiException) as caught:
                        Response(response)
                    self.assertEqual(caught.exception.http_status_code, status)
                    self.assertEqual(caught.exception.url, response.url)

    def test_empty_success_remains_valid(self) -> None:
        for status in (200, 201, 204):
            with self.subTest(status=status):
                response = requests.Response()
                response.status_code = status
                response.url = "https://api.sift.com/v205/events"
                response._content = b""
                result = Response(response)
                self.assertEqual(result.http_status_code, status)
                self.assertIsNone(result.body)

    def test_public_track_propagates_empty_server_error(self) -> None:
        response = requests.Response()
        response.status_code = 503
        response.url = "https://api.sift.com/v205/events"
        response._content = b""
        with requests.Session() as session:
            with mock.patch.object(
                session, "post", return_value=response
            ) as post:
                client = Client(api_key="test-key", session=session)
                with self.assertRaises(ApiException) as caught:
                    client.track("$create_account", {"$user_id": "test-user"})
        post.assert_called_once()
        self.assertEqual(caught.exception.http_status_code, 503)
