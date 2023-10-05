import datetime
from decimal import Decimal
import warnings
import json
import mock
import sift
import unittest
import sys
import requests.exceptions
if sys.version_info[0] < 3:
    import six.moves.urllib as urllib 
else:
    import urllib.parse


def valid_transaction_properties():
    return {
        '$buyer_user_id': '123456',
        '$seller_user_id': '654321',
        '$amount': Decimal('1253200.0'),
        '$currency_code': 'USD',
        '$time': int(datetime.datetime.now().strftime('%S')),
        '$transaction_id': 'my_transaction_id',
        '$billing_name': 'Mike Snow',
        '$billing_bin': '411111',
        '$billing_last4': '1111',
        '$billing_address1': '123 Main St.',
        '$billing_city': 'San Francisco',
        '$billing_region': 'CA',
        '$billing_country': 'US',
        '$billing_zip': '94131',
        '$user_email': 'mike@example.com'
    }


def valid_label_properties():
    return {
        '$description': 'Listed a fake item',
        '$is_bad': True,
        '$reasons': ["$fake"],
        '$source': 'Internal Review Queue',
        '$analyst': 'super.sleuth@example.com'
    }


def score_response_json():
    return """{
      "status": 0,
      "error_message": "OK",
      "user_id": "12345",
      "score": 0.55
    }"""


def action_response_json():
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
        "score": 0.55,
        "status": 0,
        "error_message": "OK",
        "user_id": "Fred"
    }"""


def response_with_data_header():
    return {
        'content-length': 1,         # Simply has to be > 0
        'content-type': 'application/json; charset=UTF-8'
    }


class TestSiftPythonClient(unittest.TestCase):

    def setUp(self):
        self.test_key = 'a_fake_test_api_key'
        self.sift_client = sift.Client(self.test_key, version='203')
        self.sift_client_v204 = sift.Client(self.test_key)

    def test_track_requires_valid_event(self):
        self.assertRaises(TypeError, self.sift_client.track, None, {})
        self.assertRaises(ValueError, self.sift_client.track, '', {})
        self.assertRaises(TypeError, self.sift_client_v204.track, 42, {'version': '203'})

    def test_track_requires_properties(self):
        event = 'custom_event'
        self.assertRaises(TypeError, self.sift_client.track, event, None, {})
        self.assertRaises(TypeError, self.sift_client_v204.track, event, 42, {'version': '203'})
        self.assertRaises(ValueError, self.sift_client.track, event, {})

    def test_score_requires_user_id(self):
        self.assertRaises(TypeError, self.sift_client_v204.score, None, {'version': '203'})
        self.assertRaises(ValueError, self.sift_client.score, '', {})
        self.assertRaises(TypeError, self.sift_client.score, 42, {})

    def test_event_ok(self):
        event = '$transaction'
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, 'post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.track(event, valid_transaction_properties())
            mock_post.assert_called_with(
                'https://api.siftscience.com/v203/events',
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={})
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")

    def test_event_with_timeout_param_ok(self):
        event = '$transaction'
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client_v204.session, 'post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client_v204.track(
                event, valid_transaction_properties(), timeout=test_timeout, version='203')
            mock_post.assert_called_with(
                'https://api.siftscience.com/v203/events',
                data=mock.ANY,
                headers=mock.ANY,
                timeout=test_timeout,
                params={})
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")

    def test_score_ok(self):
        mock_response = mock.Mock()
        mock_response.content = score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client_v204.session, 'get') as mock_get:
            mock_get.return_value = mock_response
            response = self.sift_client_v204.score('12345', version='203')
            mock_get.assert_called_with(
                'https://api.siftscience.com/v203/score/12345',
                params={'api_key': self.test_key},
                headers=mock.ANY,
                timeout=mock.ANY)
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_error_message == "OK")
            assert(response.body['score'] == 0.55)

    def test_score_with_timeout_param_ok(self):
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, 'get') as mock_get:
            mock_get.return_value = mock_response
            response = self.sift_client.score('12345', test_timeout)
            mock_get.assert_called_with(
                'https://api.siftscience.com/v203/score/12345',
                params={'api_key': self.test_key},
                headers=mock.ANY,
                timeout=test_timeout)
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_error_message == "OK")
            assert(response.body['score'] == 0.55)

    def test_sync_score_ok(self):
        event = '$transaction'
        mock_response = mock.Mock()
        mock_response.content = ('{"status": 0, "error_message": "OK", "score_response": %s}'
                                 % score_response_json())
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, 'post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.track(
                event, valid_transaction_properties(), return_score=True)
            mock_post.assert_called_with(
                'https://api.siftscience.com/v203/events',
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={'return_score': 'true'})
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")
            assert(response.body["score_response"]['score'] == 0.55)

    def test_label_user_ok(self):
        user_id = '54321'
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, 'post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.label(user_id, valid_label_properties())
            properties = {
                '$description': 'Listed a fake item',
                '$is_bad': True,
                '$reasons': ["$fake"],
                '$source': 'Internal Review Queue',
                '$analyst': 'super.sleuth@example.com'
            }
            properties.update({'$api_key': self.test_key, '$type': '$label'})
            data = json.dumps(properties)
            mock_post.assert_called_with(
                'https://api.siftscience.com/v203/users/%s/labels' % user_id,
                data=data, headers=mock.ANY, timeout=mock.ANY, params={})
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")

    def test_label_user_with_timeout_param_ok(self):
        user_id = '54321'
        test_timeout = 5
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client_v204.session, 'post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client_v204.label(
                user_id, valid_label_properties(), test_timeout, version='203')
            properties = {
                '$description': 'Listed a fake item',
                '$is_bad': True,
                '$reasons': ["$fake"],
                '$source': 'Internal Review Queue',
                '$analyst': 'super.sleuth@example.com'
            }
            properties.update({'$api_key': self.test_key, '$type': '$label'})
            data = json.dumps(properties)
            mock_post.assert_called_with(
                'https://api.siftscience.com/v203/users/%s/labels' % user_id,
                data=data, headers=mock.ANY, timeout=test_timeout, params={})
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")

    def test_unlabel_user_ok(self):
        user_id = '54321'
        mock_response = mock.Mock()
        mock_response.status_code = 204
        with mock.patch.object(self.sift_client.session, 'delete') as mock_delete:
            mock_delete.return_value = mock_response
            response = self.sift_client.unlabel(user_id)
            mock_delete.assert_called_with(
                'https://api.siftscience.com/v203/users/%s/labels' % user_id,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={'api_key': self.test_key})
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())

    def test_unicode_string_parameter_support(self):
        # str is unicode in python 3, so no need to check as this was covered
        # by other unit tests.
        if sys.version_info[0] < 3:
            mock_response = mock.Mock()
            mock_response.content = '{"status": 0, "error_message": "OK"}'
            mock_response.json.return_value = json.loads(mock_response.content)
            mock_response.status_code = 200
            mock_response.headers = response_with_data_header()

            user_id = '23056'

            with mock.patch.object(self.sift_client.session, 'post') as mock_post:
                mock_post.return_value = mock_response
                assert(
                    self.sift_client.track(
                        '$transaction',
                        valid_transaction_properties()))
                assert(
                    self.sift_client.label(
                        user_id,
                        valid_label_properties()))
            with mock.patch.object(self.sift_client.session, 'get') as mock_get:
                mock_get.return_value = mock_response
                assert(self.sift_client.score(user_id))

    def test_unlabel_user_with_special_chars_ok(self):
        user_id = "54321=.-_+@:&^%!$"
        mock_response = mock.Mock()
        mock_response.status_code = 204
        with mock.patch.object(self.sift_client_v204.session, 'delete') as mock_delete:
            mock_delete.return_value = mock_response
            response = self.sift_client_v204.unlabel(user_id, version='203')
            mock_delete.assert_called_with(
                'https://api.siftscience.com/v203/users/%s/labels' % urllib.parse.quote(user_id),
                headers=mock.ANY,
                timeout=mock.ANY,
                params={'api_key': self.test_key})
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())

    def test_label_user__with_special_chars_ok(self):
        user_id = '54321=.-_+@:&^%!$'
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, 'post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.label(
                user_id, valid_label_properties())
            properties = {
                '$description': 'Listed a fake item',
                '$is_bad': True,
                '$reasons': ["$fake"],
                '$source': 'Internal Review Queue',
                '$analyst': 'super.sleuth@example.com'
            }
            properties.update({'$api_key': self.test_key, '$type': '$label'})
            data = json.dumps(properties)
            mock_post.assert_called_with(
                'https://api.siftscience.com/v203/users/%s/labels' % urllib.parse.quote(user_id),
                data=data,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={})
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")

    def test_score__with_special_user_id_chars_ok(self):
        user_id = '54321=.-_+@:&^%!$'
        mock_response = mock.Mock()
        mock_response.content = score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()
        with mock.patch.object(self.sift_client.session, 'get') as mock_get:
            mock_get.return_value = mock_response
            response = self.sift_client.score(user_id)
            mock_get.assert_called_with(
                'https://api.siftscience.com/v203/score/%s' % urllib.parse.quote(user_id),
                params={'api_key': self.test_key},
                headers=mock.ANY,
                timeout=mock.ANY)
            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_error_message == "OK")
            assert(response.body['score'] == 0.55)

    def test_exception_during_track_call(self):
        warnings.simplefilter("always")
        with mock.patch.object(self.sift_client.session, 'post') as mock_post:
            mock_post.side_effect = mock.Mock(
                side_effect=requests.exceptions.RequestException("Failed"))
            self.assertRaises(
                sift.client.ApiException, self.sift_client.track,
                '$transaction', valid_transaction_properties())

    def test_exception_during_score_call(self):
        warnings.simplefilter("always")
        with mock.patch.object(self.sift_client.session, 'get') as mock_get:
            mock_get.side_effect = mock.Mock(
                side_effect=requests.exceptions.RequestException("Failed"))
            self.assertRaises(
                sift.client.ApiException, self.sift_client.score, 'Fred')

    def test_exception_during_unlabel_call(self):
        warnings.simplefilter("always")
        with mock.patch.object(self.sift_client.session, 'delete') as mock_delete:
            mock_delete.side_effect = mock.Mock(
                side_effect=requests.exceptions.RequestException("Failed"))
            self.assertRaises(
                sift.client.ApiException, self.sift_client.unlabel, 'Fred')

    def test_return_actions_on_track(self):
        event = '$transaction'
        mock_response = mock.Mock()
        mock_response.content = ('{"status": 0, "error_message": "OK", "score_response": %s}'
                                 % action_response_json())
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        mock_response.headers = response_with_data_header()

        with mock.patch.object(self.sift_client.session, 'post') as mock_post:
            mock_post.return_value = mock_response

            response = self.sift_client.track(
                event, valid_transaction_properties(), return_action=True)
            mock_post.assert_called_with(
                'https://api.siftscience.com/v203/events',
                data=mock.ANY,
                headers=mock.ANY,
                timeout=mock.ANY,
                params={'return_action': 'true'})

            self.assertIsInstance(response, sift.client.Response)
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")

            actions = response.body["score_response"]['actions']
            assert(actions)
            assert(actions[0]['action'])
            assert(actions[0]['action']['id'] == 'freds_action')
            assert(actions[0]['triggers'])


def main():
    unittest.main()

if __name__ == '__main__':
    main()
