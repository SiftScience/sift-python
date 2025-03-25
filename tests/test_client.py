from __future__ import annotations

import datetime
import json
import typing as t
import warnings
from decimal import Decimal
from unittest import TestCase, mock

from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

import sift
from sift.utils import quote_path as _q


def valid_transaction_properties() -> dict[str, t.Any]:
    return {
        "$buyer_user_id": "123456",
        "$seller_user_id": "654321",
        "$amount": Decimal("1253200.0"),
        "$currency_code": "USD",
        "$time": int(datetime.datetime.now().strftime("%S")),
        "$transaction_id": "my_transaction_id",
        "$billing_name": "Mike Snow",
        "$billing_bin": "411111",
        "$billing_last4": "1111",
        "$billing_address1": "123 Main St.",
        "$billing_city": "San Francisco",
        "$billing_region": "CA",
        "$billing_country": "US",
        "$billing_zip": "94131",
        "$user_email": "mike@example.com",
    }


def valid_label_properties() -> dict[str, t.Any]:
    return {
        "$abuse_type": "content_abuse",
        "$is_bad": True,
        "$description": "Listed a fake item",
        "$source": "Internal Review Queue",
        "$analyst": "super.sleuth@example.com",
    }


def valid_psp_merchant_properties() -> dict[str, t.Any]:
    return {
        "$id": "api-key-1",
        "$name": "Wonderful Payments Inc.",
        "$description": "Wonderful Payments payment provider.",
        "$address": {
            "$name": "Alany",
            "$address_1": "Big Payment blvd, 22",
            "$address_2": "apt, 8",
            "$city": "New Orleans",
            "$region": "NA",
            "$country": "US",
            "$zipcode": "76830",
            "$phone": "0394888320",
        },
        "$category": "1002",
        "$service_level": "Platinum",
        "$status": "active",
        "$risk_profile": {"$level": "low", "$score": 10},
    }


def valid_psp_merchant_properties_response() -> str:
    return """{
        "id":"api-key-1",
        "name": "Wonderful Payments Inc.",
        "description": "Wonderful Payments payment provider.",
        "category": "1002",
        "service_level": "Platinum",
        "status": "active",
        "risk_profile": {
            "level": "low",
            "score": "10"
        },
        "address": {
            "name": "Alany",
            "address_1": "Big Payment blvd, 22",
            "address_2": "apt, 8",
            "city": "New Orleans",
            "region": "NA",
            "country": "US",
            "zipcode": "76830",
            "phone": "0394888320"
        }
    }"""


def score_response_json() -> str:
    return """{
      "status": 0,
      "error_message": "OK",
      "user_id": "12345",
      "score": 0.85,
      "latest_label": {
        "is_bad": true,
        "time": 1450201660000
      },
      "scores": {
        "content_abuse": {
          "score": 0.14
        },
        "payment_abuse": {
          "score": 0.97
        }
      },
      "latest_labels": {
        "promotion_abuse": {
          "is_bad": false,
          "time": 1457201099000
        },
        "payment_abuse": {
          "is_bad": true,
          "time": 1457212345000
        }
      }
    }"""


def workflow_statuses_json() -> str:
    return """{
      "route" : {
        "name" : "my route"
      },
      "history": [
        {
          "app": "decision",
          "name": "Order Looks OK",
          "state": "running",
          "config": {
            "decision_id": "order_looks_ok_payment_abuse"
          }
        }
      ]
    }"""


# A sample response from the /{version}/users/{userId}/score API.
USER_SCORE_RESPONSE_JSON = """{
  "status": 0,
  "error_message": "OK",
  "entity_type": "user",
  "entity_id": "12345",
  "scores": {
    "content_abuse": {
      "score": 0.14
    },
    "payment_abuse": {
      "score": 0.97
    }
  },
  "latest_decisions": {
    "payment_abuse": {
      "id": "user_looks_bad_payment_abuse",
      "category": "block",
      "source": "AUTOMATED_RULE",
      "time": 1352201880,
      "description": "Bad Fraudster"
    }
  },
  "latest_labels": {
    "promotion_abuse": {
      "is_bad": false,
      "time": 1457201099000
    },
    "payment_abuse": {
      "is_bad": true,
      "time": 1457212345000
    }
  }
}"""


def action_response_json() -> str:
    return """{
        "actions": [
            {
                "action": {
                    "id": "freds_action"
                },
                "entity": {
                    "id": "Fred"
                },
                "id": "ACTION1234567890:freds_action",
                "triggers": [
                    {
                        "source": "synchronous_action",
                        "trigger": {
                            "id": "TRIGGER1234567890"
                        },
                        "type": "formula"
                    }
                ]
            }
        ],
        "score": 0.85,
        "status": 0,
        "error_message": "OK",
        "user_id": "Fred",
        "scores": {
          "content_abuse": {
            "score": 0.14
          },
          "payment_abuse": {
            "score": 0.97
          }
        },
        "latest_labels": {
          "promotion_abuse": {
            "is_bad": false,
            "time": 1457201099000
          },
          "payment_abuse": {
            "is_bad": true,
            "time": 1457212345000
          }
        }
      }"""


def response_with_data_header() -> dict[str, t.Any]:
    return {"content-type": "application/json; charset=UTF-8"}


class TestSiftPythonClient(TestCase):

    def setUp(self) -> None:
        self.test_key = "a_fake_test_api_key"
        self.account_id = "ACCT"
        self.sift_client = sift.Client(
            api_key=self.test_key,
            account_id=self.account_id,
        )

    def test_global_api_key(self) -> None:
        # test for error if global key is undefined
        with mock.patch("sift.api_key"):
            self.assertRaises(TypeError, sift.Client)

        sift.api_key = "a_test_global_api_key"
        local_api_key = "a_test_local_api_key"

        client1 = sift.Client()
        client2 = sift.Client(local_api_key)

        # test that global api key is assigned
        assert client1.api_key == sift.api_key
        # test that local api key is assigned
        assert client2.api_key == local_api_key

        client2 = sift.Client()
        # test that client2 is assigned a new object with global api_key
        assert client2.api_key == sift.api_key

    @mock.patch("sift.api_key", return_value=None)
    def test_constructor_requires_valid_api_key(self, _) -> None:
        self.assertRaises(TypeError, sift.Client, None)
        self.assertRaises(ValueError, sift.Client, "")

    def test_constructor_invalid_api_url(self) -> None:
        self.assertRaises(TypeError, sift.Client, self.test_key, None)
        self.assertRaises(ValueError, sift.Client, self.test_key, "")

    def test_constructor_api_key(self) -> None:
        client = sift.Client(self.test_key)
        self.assertEqual(client.api_key, self.test_key)

    def test_track_requires_valid_event(self) -> None:
        self.assertRaises(TypeError, self.sift_client.track, None, {})
        self.assertRaises(ValueError, self.sift_client.track, "", {})
        self.assertRaises(TypeError, self.sift_client.track, 42, {})

    def test_track_requires_properties(self) -> None:
        event = "custom_event"
        self.assertRaises(TypeError, self.sift_client.track, event, None)
        self.assertRaises(TypeError, self.sift_client.track, event, 42)
        self.assertRaises(ValueError, self.sift_client.track, event, {})

    def test_score_requires_user_id(self) -> None:
        self.assertRaises(TypeError, self.sift_client.score, None)
        self.assertRaises(ValueError, self.sift_client.score, "")
        self.assertRaises(TypeError, self.sift_client.score, 42)

    def test_event_ok(self) -> None:
        event = "$transaction"
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event, valid_transaction_properties()
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={},
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_event_with_timeout_param_ok(self) -> None:
        event = "$transaction"
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event, valid_transaction_properties(), timeout=test_timeout
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=test_timeout,
                params={},
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_score_ok(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.score("12345")

            mock_get.assert_called_with(
                "https://api.sift.com/v205/score/12345",
                params={},
                headers=mock.ANY,
                timeout=mock.ANY,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["score"] == 0.85
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97

    def test_score_with_timeout_param_ok(self) -> None:
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.score("12345", test_timeout)

            mock_get.assert_called_with(
                "https://api.sift.com/v205/score/12345",
                params={},
                headers=mock.ANY,
                timeout=test_timeout,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["score"] == 0.85
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97

    def test_get_user_score_ok(self) -> None:
        """
        Test the GET /{version}/users/{userId}/score API,
        i.e. client.get_user_score()
        """
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = USER_SCORE_RESPONSE_JSON
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_user_score("12345", test_timeout)

            mock_get.assert_called_with(
                "https://api.sift.com/v205/users/12345/score",
                params={},
                headers=mock.ANY,
                timeout=test_timeout,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["entity_id"] == "12345"
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97
            assert "latest_decisions" in response.body

    def test_get_user_score_with_abuse_types_ok(self) -> None:
        """
        Test the GET /{version}/users/{userId}/score?abuse_types=... API,
        i.e. client.get_user_score()
        """
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = USER_SCORE_RESPONSE_JSON
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_user_score(
                "12345",
                abuse_types=["payment_abuse", "content_abuse"],
                timeout=test_timeout,
            )

            mock_get.assert_called_with(
                "https://api.sift.com/v205/users/12345/score",
                params={"abuse_types": "payment_abuse,content_abuse"},
                headers=mock.ANY,
                timeout=test_timeout,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["entity_id"] == "12345"
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97
            assert "latest_decisions" in response.body

    def test_rescore_user_ok(self) -> None:
        """
        Test the POST /{version}/users/{userId}/score API,
        i.e. client.rescore_user()
        """
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = USER_SCORE_RESPONSE_JSON
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.rescore_user("12345", test_timeout)

            mock_post.assert_called_with(
                "https://api.sift.com/v205/users/12345/score",
                params={},
                headers=mock.ANY,
                timeout=test_timeout,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["entity_id"] == "12345"
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97
            assert "latest_decisions" in response.body

    def test_rescore_user_with_abuse_types_ok(self) -> None:
        """
        Test the POST /{version}/users/{userId}/score?abuse_types=... API,
        i.e. client.rescore_user()
        """
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = USER_SCORE_RESPONSE_JSON
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.rescore_user(
                "12345",
                abuse_types=["payment_abuse", "content_abuse"],
                timeout=test_timeout,
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/users/12345/score",
                params={"abuse_types": "payment_abuse,content_abuse"},
                headers=mock.ANY,
                timeout=test_timeout,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["entity_id"] == "12345"
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97
            assert "latest_decisions" in response.body

    def test_sync_score_ok(self) -> None:
        event = "$transaction"
        mock_response = mock.Mock()
        mock_response.content = f'{{"status": 0, "error_message": "OK", "score_response": {score_response_json()}}}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event,
                valid_transaction_properties(),
                return_score=True,
                abuse_types=["payment_abuse", "content_abuse", "legacy"],
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={
                    "return_score": "true",
                    "abuse_types": "payment_abuse,content_abuse,legacy",
                },
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["score_response"]["score"] == 0.85
            assert (
                response.body["score_response"]["scores"]["content_abuse"][
                    "score"
                ]
                == 0.14
            )
            assert (
                response.body["score_response"]["scores"]["payment_abuse"][
                    "score"
                ]
                == 0.97
            )

    def test_sync_workflow_ok(self) -> None:
        event = "$transaction"
        mock_response = mock.Mock()
        mock_response.content = f'{{"status": 0, "error_message": "OK", "workflow_statuses": {workflow_statuses_json()}}}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event,
                valid_transaction_properties(),
                return_workflow_status=True,
                return_route_info=True,
                abuse_types=["payment_abuse", "content_abuse", "legacy"],
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={
                    "return_workflow_status": "true",
                    "return_route_info": "true",
                    "abuse_types": "payment_abuse,content_abuse,legacy",
                },
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert (
                response.body["workflow_statuses"]["route"]["name"]
                == "my route"
            )

    def test_get_decisions_fails(self) -> None:
        with self.assertRaises(ValueError):
            self.sift_client.get_decisions(
                t.cast(t.Literal["user", "order", "session", "content"], "usr")
            )

    def test_get_decisions(self) -> None:
        mock_response = mock.Mock()

        get_decisions_response_json = """
        {
            "data": [
                {
                    "id": "block_user",
                    "name": "Block user",
                    "description": "user has a different billing and shipping addresses",
                    "entity_type": "user",
                    "abuse_type": "legacy",
                    "category": "block",
                    "webhook_url": "http://web.hook",
                    "created_at": "1468005577348",
                    "created_by": "admin@biz.com",
                    "updated_at": "1469229177756",
                    "updated_by": "analyst@biz.com"
                }
            ],
            "has_more": "true",
            "next_ref": "v3/accounts/accountId/decisions"
        }
        """
        mock_response.content = get_decisions_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_decisions(
                entity_type="user",
                limit=10,
                start_from=None,
                abuse_types="legacy,payment_abuse",
                timeout=3,
            )

            mock_get.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/decisions",
                headers=mock.ANY,
                auth=mock.ANY,
                params={
                    "entity_type": "user",
                    "limit": 10,
                    "abuse_types": "legacy,payment_abuse",
                },
                timeout=3,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert isinstance(response.body, dict)
            assert response.body["data"][0]["id"] == "block_user"

    def test_get_decisions_entity_session(self) -> None:
        mock_response = mock.Mock()
        get_decisions_response_json = """
        {
            "data": [
                {
                    "id": "block_session",
                    "name": "Block session",
                    "description": "session has problems",
                    "entity_type": "session",
                    "abuse_type": "legacy",
                    "category": "block",
                    "webhook_url": "http://web.hook",
                    "created_at": "1468005577348",
                    "created_by": "admin@biz.com",
                    "updated_at": "1469229177756",
                    "updated_by": "analyst@biz.com"
                }
            ],
            "has_more": "true",
            "next_ref": "v3/accounts/accountId/decisions"
        }
        """
        mock_response.content = get_decisions_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_decisions(
                entity_type="session",
                limit=10,
                start_from=None,
                abuse_types="account_takeover",
                timeout=3,
            )

            mock_get.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/decisions",
                headers=mock.ANY,
                auth=mock.ANY,
                params={
                    "entity_type": "session",
                    "limit": 10,
                    "abuse_types": "account_takeover",
                },
                timeout=3,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert isinstance(response.body, dict)
            assert response.body["data"][0]["id"] == "block_session"

    def test_apply_decision_to_user_ok(self) -> None:
        user_id = "54321"
        mock_response = mock.Mock()
        apply_decision_request = {
            "decision_id": "user_looks_ok_legacy",
            "source": "MANUAL_REVIEW",
            "analyst": "analyst@biz.com",
            "description": "called user and verified account",
            "time": 1481569575,
        }
        apply_decision_response_json = """
        {
            "entity": {
                "id": "54321",
                "type": "user"
            },
            "decision": {
                "id": "user_looks_ok_legacy"
            },
            "time": "1481569575"
        }
        """
        mock_response.content = apply_decision_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.apply_user_decision(
                user_id, apply_decision_request
            )

            mock_post.assert_called_with(
                f"https://api.sift.com/v3/accounts/ACCT/users/{user_id}/decisions",
                auth=mock.ANY,
                data=json.dumps(apply_decision_request),
                headers=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.http_status_code == 200
            assert isinstance(response.body, dict)
            assert response.body["entity"]["type"] == "user"

    def test_validate_no_user_id_string_fails(self) -> None:
        apply_decision_request = {
            "decision_id": "user_looks_ok_legacy",
            "source": "MANUAL_REVIEW",
            "analyst": "analyst@biz.com",
            "description": "called user and verified account",
        }

        with self.assertRaises(TypeError):
            self.sift_client._validate_apply_decision_request(
                apply_decision_request, t.cast(str, 123)
            )

    def test_apply_decision_to_order_fails_with_no_order_id(self) -> None:
        with self.assertRaises(TypeError):
            self.sift_client.apply_order_decision(
                "user_id", t.cast(str, None), {}
            )

    def test_apply_decision_to_session_fails_with_no_session_id(self) -> None:
        with self.assertRaises(TypeError):
            self.sift_client.apply_session_decision(
                "user_id", t.cast(str, None), {}
            )

    def test_get_session_decisions_fails_with_no_session_id(self) -> None:
        with self.assertRaises(TypeError):
            self.sift_client.get_session_decisions(
                "user_id", t.cast(str, None)
            )

    def test_apply_decision_to_content_fails_with_no_content_id(self) -> None:
        with self.assertRaises(TypeError):
            self.sift_client.apply_content_decision(
                "user_id", t.cast(str, None), {}
            )

    def test_validate_apply_decision_request_no_analyst_fails(self) -> None:
        apply_decision_request = {
            "decision_id": "user_looks_ok_legacy",
            "source": "MANUAL_REVIEW",
            "time": 1481569575,
        }

        with self.assertRaises(ValueError):
            self.sift_client._validate_apply_decision_request(
                apply_decision_request, "userId"
            )

    def test_validate_apply_decision_request_no_source_fails(self) -> None:
        apply_decision_request = {
            "decision_id": "user_looks_ok_legacy",
            "time": 1481569575,
        }

        with self.assertRaises(ValueError):
            self.sift_client._validate_apply_decision_request(
                apply_decision_request, "userId"
            )

    def test_validate_empty_apply_decision_request_fails(self) -> None:
        apply_decision_request: dict[str, t.Any] = {}

        with self.assertRaises(ValueError):
            self.sift_client._validate_apply_decision_request(
                apply_decision_request, "userId"
            )

    def test_apply_decision_manual_review_no_analyst_fails(self) -> None:
        user_id = "54321"
        apply_decision_request = {
            "decision_id": "user_looks_ok_legacy",
            "source": "MANUAL_REVIEW",
            "time": 1481569575,
        }

        with self.assertRaises(ValueError):
            self.sift_client.apply_user_decision(
                user_id, apply_decision_request
            )

    def test_apply_decision_no_source_fails(self) -> None:
        user_id = "54321"
        apply_decision_request = {
            "decision_id": "user_looks_ok_legacy",
            "time": 1481569575,
        }

        with self.assertRaises(ValueError):
            self.sift_client.apply_user_decision(
                user_id, apply_decision_request
            )

    def test_apply_decision_invalid_source_fails(self) -> None:
        user_id = "54321"
        apply_decision_request = {
            "decision_id": "user_looks_ok_legacy",
            "source": "INVALID_SOURCE",
            "time": 1481569575,
        }

        self.assertRaises(
            ValueError,
            self.sift_client.apply_user_decision,
            user_id,
            apply_decision_request,
        )

    def test_apply_decision_to_order_ok(self) -> None:
        user_id = "54321"
        order_id = "43210"
        mock_response = mock.Mock()
        apply_decision_request = {
            "decision_id": "order_looks_bad_payment_abuse",
            "source": "AUTOMATED_RULE",
            "time": 1481569575,
        }

        apply_decision_response_json = """
        {
            "entity": {
                "id": "54321",
                "type": "order"
            },
            "decision": {
                "id": "order_looks_bad_payment_abuse"
            },
            "time": "1481569575"
        }
        """
        mock_response.content = apply_decision_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.apply_order_decision(
                user_id, order_id, apply_decision_request
            )

            mock_post.assert_called_with(
                f"https://api.sift.com/v3/accounts/ACCT/users/{user_id}/orders/{order_id}/decisions",
                auth=mock.ANY,
                data=json.dumps(apply_decision_request),
                headers=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.http_status_code == 200
            assert isinstance(response.body, dict)
            assert response.body["entity"]["type"] == "order"

    def test_apply_decision_to_session_ok(self) -> None:
        user_id = "54321"
        session_id = "gigtleqddo84l8cm15qe4il"
        mock_response = mock.Mock()
        apply_decision_request = {
            "decision_id": "session_looks_bad_ato",
            "source": "AUTOMATED_RULE",
            "time": 1481569575,
        }

        apply_decision_response_json = """
        {
            "entity": {
                "id": "54321",
                "type": "login"
            },
            "decision": {
                "id": "session_looks_bad_ato"
            },
            "time": "1481569575"
        }
        """
        mock_response.content = apply_decision_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.apply_session_decision(
                user_id, session_id, apply_decision_request
            )

            mock_post.assert_called_with(
                f"https://api.sift.com/v3/accounts/ACCT/users/{user_id}/sessions/{session_id}/decisions",
                auth=mock.ANY,
                data=json.dumps(apply_decision_request),
                headers=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.http_status_code == 200
            assert isinstance(response.body, dict)
            assert response.body["entity"]["type"] == "login"

    def test_apply_decision_to_content_ok(self) -> None:
        user_id = "54321"
        content_id = "listing-1231"
        mock_response = mock.Mock()
        apply_decision_request = {
            "decision_id": "content_looks_bad_content_abuse",
            "source": "AUTOMATED_RULE",
            "time": 1481569575,
        }

        apply_decision_response_json = """
        {
            "entity": {
                "id": "54321",
                "type": "create_content"
            },
            "decision": {
                "id": "content_looks_bad_content_abuse"
            },
            "time": "1481569575"
        }
        """
        mock_response.content = apply_decision_response_json
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.apply_content_decision(
                user_id, content_id, apply_decision_request
            )

            mock_post.assert_called_with(
                f"https://api.sift.com/v3/accounts/ACCT/users/{user_id}/content/{content_id}/decisions",
                auth=mock.ANY,
                data=json.dumps(apply_decision_request),
                headers=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.http_status_code == 200
            assert isinstance(response.body, dict)
            assert response.body["entity"]["type"] == "create_content"

    def test_label_user_ok(self) -> None:
        user_id = "54321"
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.label(
                user_id, valid_label_properties()
            )

            properties = {
                "$abuse_type": "content_abuse",
                "$is_bad": True,
                "$description": "Listed a fake item",
                "$source": "Internal Review Queue",
                "$analyst": "super.sleuth@example.com",
                "$api_key": self.test_key,
                "$type": "$label",
            }

            mock_post.assert_called_with(
                f"https://api.sift.com/v205/users/{user_id}/labels",
                data=json.dumps(properties),
                headers=mock.ANY,
                timeout=mock.ANY,
                params={},
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_label_user_with_timeout_param_ok(self) -> None:
        user_id = "54321"
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.label(
                user_id, valid_label_properties(), test_timeout
            )

            properties = {
                "$abuse_type": "content_abuse",
                "$is_bad": True,
                "$description": "Listed a fake item",
                "$source": "Internal Review Queue",
                "$analyst": "super.sleuth@example.com",
                "$api_key": self.test_key,
                "$type": "$label",
            }

            mock_post.assert_called_with(
                f"https://api.sift.com/v205/users/{user_id}/labels",
                data=json.dumps(properties),
                headers=mock.ANY,
                timeout=test_timeout,
                params={},
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_unlabel_user_ok(self) -> None:
        user_id = "54321"
        mock_response = mock.Mock()
        mock_response.status_code = 204

        with mock.patch.object(
            self.sift_client.session, "delete"
        ) as mock_delete:
            mock_delete.return_value = mock_response

            response = self.sift_client.unlabel(
                user_id, abuse_type="account_abuse"
            )

            mock_delete.assert_called_with(
                f"https://api.sift.com/v205/users/{user_id}/labels",
                headers=mock.ANY,
                timeout=mock.ANY,
                params={"abuse_type": "account_abuse"},
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()

    def test_unlabel_user_with_special_chars_ok(self) -> None:
        user_id = "54321=.-_+@:&^%!$"
        mock_response = mock.Mock()
        mock_response.status_code = 204

        with mock.patch.object(
            self.sift_client.session, "delete"
        ) as mock_delete:
            mock_delete.return_value = mock_response

            response = self.sift_client.unlabel(user_id)

            mock_delete.assert_called_with(
                f"https://api.sift.com/v205/users/{_q(user_id)}/labels",
                headers=mock.ANY,
                timeout=mock.ANY,
                params={},
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()

    def test_label_user__with_special_chars_ok(self) -> None:
        user_id = "54321=.-_+@:&^%!$"
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.label(
                user_id, valid_label_properties()
            )

            properties = {
                "$abuse_type": "content_abuse",
                "$is_bad": True,
                "$description": "Listed a fake item",
                "$source": "Internal Review Queue",
                "$analyst": "super.sleuth@example.com",
                "$api_key": self.test_key,
                "$type": "$label",
            }

            mock_post.assert_called_with(
                f"https://api.sift.com/v205/users/{_q(user_id)}/labels",
                data=json.dumps(properties),
                headers=mock.ANY,
                timeout=mock.ANY,
                params={},
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_score__with_special_user_id_chars_ok(self) -> None:
        user_id = "54321=.-_+@:&^%!$"
        mock_response = mock.Mock()
        mock_response.content = score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.score(user_id, abuse_types=["legacy"])

            mock_get.assert_called_with(
                f"https://api.sift.com/v205/score/{_q(user_id)}",
                params={"abuse_types": "legacy"},
                headers=mock.ANY,
                timeout=mock.ANY,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["score"] == 0.85
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97

    def test_exception_during_track_call(self) -> None:
        warnings.simplefilter("always")

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.side_effect = mock.Mock(
                side_effect=RequestException("Failed")
            )

            with self.assertRaises(sift.client.ApiException):
                self.sift_client.track(
                    "$transaction", valid_transaction_properties()
                )

    def test_exception_during_score_call(self) -> None:
        warnings.simplefilter("always")

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.side_effect = mock.Mock(
                side_effect=RequestException("Failed")
            )

            with self.assertRaises(sift.client.ApiException):
                self.sift_client.score("Fred")

    def test_exception_during_unlabel_call(self) -> None:
        warnings.simplefilter("always")

        with mock.patch.object(
            self.sift_client.session, "delete"
        ) as mock_delete:
            mock_delete.side_effect = mock.Mock(
                side_effect=RequestException("Failed")
            )

            with self.assertRaises(sift.client.ApiException):
                self.sift_client.unlabel("Fred")

    def test_return_actions_on_track(self) -> None:
        event = "$transaction"
        mock_response = mock.Mock()
        mock_response.content = f'{{"status": 0, "error_message": "OK", "score_response": {action_response_json()}}}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event, valid_transaction_properties(), return_action=True
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={"return_action": "true"},
            )

            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)

            actions = response.body["score_response"]["actions"]
            assert actions
            assert actions[0]["action"]
            assert actions[0]["action"]["id"] == "freds_action"
            assert actions[0]["triggers"]

    def test_get_workflow_status(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = """
        {
            "id": "4zxwibludiaaa",
            "config": {
                "id": "5rrbr4iaaa",
                "version": "1468367620871"
            },
            "config_display_name": "workflow config",
            "abuse_types": [
                "payment_abuse"
            ],
            "state": "running",
            "entity": {
                "id": "example_user",
                "type": "user"
            },
            "history": [
                {
                    "app": "decision",
                    "name": "decision",
                    "state": "running",
                    "config": {
                        "decision_id": "user_decision"
                    }
                },
                {
                    "app": "event",
                    "name": "Event",
                    "state": "finished",
                    "config": {}
                },
                {
                    "app": "user",
                    "name": "Entity",
                    "state": "finished",
                    "config": {}
                }
            ]
        }
        """
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_workflow_status(
                "4zxwibludiaaa", timeout=3
            )

            mock_get.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/workflows/runs/4zxwibludiaaa",
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=3,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert isinstance(response.body, dict)
            assert response.body["state"] == "running"

    def test_get_user_decisions(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = """
        {
            "decisions": {
                "payment_abuse": {
                    "decision": {
                        "id": "user_decision"
                    },
                    "time": 1468707128659,
                    "webhook_succeeded": false
                }
            }
        }
        """
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_user_decisions("example_user")

            mock_get.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/users/example_user/decisions",
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert isinstance(response.body, dict)
            assert (
                response.body["decisions"]["payment_abuse"]["decision"]["id"]
                == "user_decision"
            )

    def test_get_order_decisions(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = """
        {
            "decisions": {
                "payment_abuse": {
                    "decision": {
                        "id": "decision7"
                    },
                    "time": 1468599638005,
                    "webhook_succeeded": false
                },
                "promotion_abuse": {
                    "decision": {
                        "id": "good_order"
                    },
                    "time": 1468517407135,
                    "webhook_succeeded": true
                }
            }
        }
        """
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_order_decisions("example_order")

            mock_get.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/orders/example_order/decisions",
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert isinstance(response.body, dict)
            assert (
                response.body["decisions"]["payment_abuse"]["decision"]["id"]
                == "decision7"
            )
            assert (
                response.body["decisions"]["promotion_abuse"]["decision"]["id"]
                == "good_order"
            )

    def test_get_session_decisions(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = """
        {
            "decisions": {
                "account_takeover": {
                    "decision": {
                        "id": "session_decision"
                    },
                    "time": 1461963839151,
                    "webhook_succeeded": true
                }
            }
        }
        """
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_session_decisions(
                "example_user", "example_session"
            )

            mock_get.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/users/example_user/sessions/example_session/decisions",
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert isinstance(response.body, dict)
            assert (
                response.body["decisions"]["account_takeover"]["decision"][
                    "id"
                ]
                == "session_decision"
            )

    def test_get_content_decisions(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = """
        {
            "decisions": {
                "content_abuse": {
                    "decision": {
                        "id": "content_looks_bad_content_abuse"
                    },
                    "time": 1468517407135,
                    "webhook_succeeded": true
                }
            }
        }
        """
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_content_decisions(
                "example_user", "example_content"
            )

            mock_get.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/users/example_user/content/example_content/decisions",
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert isinstance(response.body, dict)
            assert (
                response.body["decisions"]["content_abuse"]["decision"]["id"]
                == "content_looks_bad_content_abuse"
            )

    def test_provided_session(self) -> None:
        session = mock.Mock()
        client = sift.Client(
            api_key=self.test_key,
            account_id=self.account_id,
            session=session,
        )

        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        session.post.return_value = mock_response
        event = "$transaction"

        client.track(event, valid_transaction_properties())

        session.post.assert_called_once()

    def test_get_psp_merchant_profile(self) -> None:
        """Test the GET /{version}/accounts/{accountId}/scorepsp_management/merchants?batch_type=..."""
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = valid_psp_merchant_properties_response()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.get_psp_merchant_profiles(
                timeout=test_timeout
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/psp_management/merchants",
                params={},
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=test_timeout,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert isinstance(response.body, dict)
            assert "address" in response.body

    def test_get_psp_merchant_profile_id(self) -> None:
        """Test the GET /{version}/accounts/{accountId}/scorepsp_management/merchants/{merchantId}"""
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = valid_psp_merchant_properties_response()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.get_a_psp_merchant_profile(
                merchant_id="api-key-1", timeout=test_timeout
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/psp_management/merchants/api-key-1",
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=test_timeout,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert isinstance(response.body, dict)
            assert "address" in response.body

    def test_create_psp_merchant_profile(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = valid_psp_merchant_properties_response()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.create_psp_merchant_profile(
                valid_psp_merchant_properties()
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/psp_management/merchants",
                data=json.dumps(valid_psp_merchant_properties()),
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert isinstance(response.body, dict)
            assert "address" in response.body

    def test_update_psp_merchant_profile(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = valid_psp_merchant_properties_response()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "put") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.update_psp_merchant_profile(
                "api-key-1", valid_psp_merchant_properties()
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v3/accounts/ACCT/psp_management/merchants/api-key-1",
                data=json.dumps(valid_psp_merchant_properties()),
                headers=mock.ANY,
                auth=mock.ANY,
                timeout=mock.ANY,
            )
            self.assertIsInstance(response, sift.client.Response)
            assert isinstance(response.body, dict)
            assert "address" in response.body

    def test_with_include_score_percentiles_ok(self) -> None:
        event = "$transaction"
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event,
                valid_transaction_properties(),
                include_score_percentiles=True,
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={"fields": "SCORE_PERCENTILES"},
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_include_score_percentiles_as_false_ok(self) -> None:
        event = "$transaction"
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event,
                valid_transaction_properties(),
                include_score_percentiles=False,
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={},
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_status == 0
            assert response.api_error_message == "OK"

    def test_score_api_include_score_percentiles_ok(self) -> None:
        mock_response = mock.Mock()
        mock_response.content = score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.score(
                user_id="12345", include_score_percentiles=True
            )

            mock_get.assert_called_with(
                "https://api.sift.com/v205/score/12345",
                params={"fields": "SCORE_PERCENTILES"},
                headers=mock.ANY,
                timeout=mock.ANY,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["score"] == 0.85
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97

    def test_get_user_score_include_score_percentiles_ok(self) -> None:
        """
        Test the GET /{version}/users/{userId}/score API,
        i.e. client.get_user_score()
        """
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = USER_SCORE_RESPONSE_JSON
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, "get") as mock_get:
            mock_get.return_value = mock_response

            response = self.sift_client.get_user_score(
                user_id="12345",
                timeout=test_timeout,
                include_score_percentiles=True,
            )

            mock_get.assert_called_with(
                "https://api.sift.com/v205/users/12345/score",
                params={"fields": "SCORE_PERCENTILES"},
                headers=mock.ANY,
                timeout=test_timeout,
                auth=HTTPBasicAuth(self.test_key, ""),
            )
            self.assertIsInstance(response, sift.client.Response)
            assert response.is_ok()
            assert response.api_error_message == "OK"
            assert isinstance(response.body, dict)
            assert response.body["entity_id"] == "12345"
            assert response.body["scores"]["content_abuse"]["score"] == 0.14
            assert response.body["scores"]["payment_abuse"]["score"] == 0.97
            assert "latest_decisions" in response.body

    def test_warnings_added_as_fields_param(self) -> None:
        event = "$transaction"
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event, valid_transaction_properties(), include_warnings=True
            )

            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={"fields": "WARNINGS"},
            )
            self.assertIsInstance(response, sift.client.Response)

    def test_warnings_and_score_percentiles_added_as_fields_param(
        self,
    ) -> None:
        event = "$transaction"
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200

        with mock.patch.object(self.sift_client.session, "post") as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.track(
                event,
                valid_transaction_properties(),
                include_score_percentiles=True,
                include_warnings=True,
            )
            mock_post.assert_called_with(
                "https://api.sift.com/v205/events",
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={"fields": "SCORE_PERCENTILES,WARNINGS"},
            )
            self.assertIsInstance(response, sift.client.Response)


def main() -> None:
    main()


if __name__ == "__main__":
    main()
