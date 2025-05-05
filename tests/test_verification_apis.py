from __future__ import annotations

import json
import typing as t
from unittest import TestCase, mock

import sift


def valid_verification_send_properties() -> dict[str, t.Any]:
    return {
        "$user_id": "billy_jones_301",
        "$send_to": "billy_jones_301@gmail.com",
        "$verification_type": "$email",
        "$brand_name": "MyTopBrand",
        "$language": "en",
        "$site_country": "IN",
        "$event": {
            "$session_id": "SOME_SESSION_ID",
            "$verified_event": "$login",
            "$verified_entity_id": "SOME_SESSION_ID",
            "$reason": "$automated_rule",
            "$ip": "192.168.1.1",
            "$browser": {
                "$user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
            },
        },
    }


def valid_verification_resend_properties() -> dict[str, t.Any]:
    return {
        "$user_id": "billy_jones_301",
        "$verified_event": "$login",
        "$verified_entity_id": "SOME_SESSION_ID",
    }


def valid_verification_check_properties() -> dict[str, t.Any]:
    return {
        "$user_id": "billy_jones_301",
        "$code": "123456",
        "$verified_event": "$login",
        "$verified_entity_id": "SOME_SESSION_ID",
    }


def response_with_data_header() -> dict[str, t.Any]:
    return {
        "content-length": 1,
        "content-type": "application/json; charset=UTF-8",
    }


class TestVerificationAPI(TestCase):
    def setUp(self) -> None:
        self.test_key = "a_fake_test_api_key"
        self.sift_client = sift.Client(self.test_key)

    def test_verification_send_ok(self) -> None:
        mock_response = mock.Mock()

        send_response_json = """
        {
            "status": 0,
            "error_message": "OK",
            "sent_at": 1689316615034,
            "segment_id": "143",
            "segment_name": "Verification Template",
            "brand_name": "",
            "site_country": "",
            "content_language": "",
            "http_status_code": 200
        }
        """

        mock_response.content = send_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.verification_send(
                valid_verification_send_properties()
            )
            data = json.dumps(valid_verification_send_properties())
            mock_post.assert_called_with(
                "https://api.sift.com/v1/verification/send",
                auth=mock.ANY,
                data=data,
                headers=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_verification_resend_ok(self) -> None:
        mock_response = mock.Mock()

        resend_response_json = """
        {
            "status": 0,
            "error_message": "OK",
            "sent_at": 1689316615034,
            "segment_id": "143",
            "segment_name": "Verification Template",
            "brand_name": "",
            "site_country": "",
            "content_language": "",
            "http_status_code": 200
        }
        """

        mock_response.content = resend_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.verification_resend(
                valid_verification_resend_properties()
            )
            data = json.dumps(valid_verification_resend_properties())
            mock_post.assert_called_with(
                "https://api.sift.com/v1/verification/resend",
                auth=mock.ANY,
                data=data,
                headers=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_verification_check_ok(self) -> None:
        mock_response = mock.Mock()

        check_response_json = """
        {
            "status": 0,
            "error_message": "OK",
            "checked_at": 1689316615034,
            "http_status_code": 200
        }
        """

        mock_response.content = check_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.verification_check(
                valid_verification_check_properties()
            )
            data = json.dumps(valid_verification_check_properties())
            mock_post.assert_called_with(
                "https://api.sift.com/v1/verification/check",
                auth=mock.ANY,
                data=data,
                headers=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"


def main() -> None:
    main()


if __name__ == "__main__":
    main()
