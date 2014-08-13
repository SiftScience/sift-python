import datetime
import json
import mock
import sift
import unittest

def valid_transaction_properties():
    return {
      '$buyer_user_id': '123456',
      '$seller_user_id': '654321',
      '$amount': 1253200,
      '$currency_code': 'USD',
      '$time': int(datetime.datetime.now().strftime('%s')),
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
      '$reasons': [ "$fake" ],
    }

def score_response_json():
    return """{
      "status":0,
      "error_message": "OK",
      "user_id":"12345",
      "score": 0.55
    }"""

class TestSiftPythonClient(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_key = 'a_fake_test_api_key'
        self.sift_client = sift.Client(self.test_key)

    def test_global_api_key(self):
        # test for error if global key is undefined
        self.assertRaises(RuntimeError, sift.Client)
        sift.api_key = "a_test_global_api_key"
        local_api_key = "a_test_local_api_key"

        client1 = sift.Client()
        client2 = sift.Client(local_api_key)
        
        # test that global api key is assigned
        assert(client1.api_key == sift.api_key)
        # test that local api key is assigned
        assert(client2.api_key == local_api_key)

        client2 = sift.Client()
        # test that client2 is assigned a new object with global api_key
        assert(client2.api_key == sift.api_key)

    def test_constructor_requires_valid_api_key(self):
        self.assertRaises(RuntimeError, sift.Client, None)
        self.assertRaises(RuntimeError, sift.Client, '')

    def test_constructor_invalid_api_url(self):
        self.assertRaises(RuntimeError, sift.Client, self.test_key, None)
        self.assertRaises(RuntimeError, sift.Client, self.test_key, '')

    def test_constructor_api_key(self):
        client = sift.Client(self.test_key)
        self.assertEqual(client.api_key, self.test_key)

    def test_track_requires_valid_event(self):
        self.assertRaises(RuntimeError, self.sift_client.track, None, {})
        self.assertRaises(RuntimeError, self.sift_client.track, '', {})
        self.assertRaises(RuntimeError, self.sift_client.track, 42, {})

    def test_track_requires_properties(self):
        event = 'custom_event'
        self.assertRaises(RuntimeError, self.sift_client.track, event, None)
        self.assertRaises(RuntimeError, self.sift_client.track, event, 42)
        self.assertRaises(RuntimeError, self.sift_client.track, event, {})

    def test_score_requires_user_id(self):
        self.assertRaises(RuntimeError, self.sift_client.score, None)
        self.assertRaises(RuntimeError, self.sift_client.score, '')
        self.assertRaises(RuntimeError, self.sift_client.score, 42)

    def test_event_ok(self):
        event = '$transaction'
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK"}'
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.track(event, valid_transaction_properties())
            mock_post.assert_called_with('https://api.siftscience.com/v203/events',
                data=mock.ANY, headers=mock.ANY, timeout=mock.ANY, params={})
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")

    def test_score_ok(self):
        mock_response = mock.Mock()
        mock_response.content = score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        with mock.patch('requests.get') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.score('12345')
            mock_post.assert_called_with('https://api.siftscience.com/v203/score/12345',
                params={'api_key':self.test_key},
                headers=mock.ANY, timeout=mock.ANY)
            assert(response.is_ok())
            assert(response.api_error_message == "OK")
            assert(response.body['score'] == 0.55)

    def test_sync_score_ok(self):
        event = '$transaction'
        mock_response = mock.Mock()
        mock_response.content = '{"status": 0, "error_message": "OK", "score_response": %s}' % score_response_json()
        mock_response.json.return_value = json.loads(mock_response.content)
        mock_response.status_code = 200
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.track(event, valid_transaction_properties(), return_score=True)
            mock_post.assert_called_with('https://api.siftscience.com/v203/events',
                data=mock.ANY, headers=mock.ANY, timeout=mock.ANY, params={'return_score': True})
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
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = mock_response
            response = self.sift_client.label(user_id, valid_label_properties())
            properties = {'$description': 'Listed a fake item', '$is_bad': True, '$reasons': [ "$fake" ]}
            properties.update({ '$api_key': self.test_key, '$type': '$label'})
            data = json.dumps(properties)
            mock_post.assert_called_with('https://api.siftscience.com/v203/users/%s/labels' % user_id,
                data=data, headers=mock.ANY, timeout=mock.ANY, params={})
            assert(response.is_ok())
            assert(response.api_status == 0)
            assert(response.api_error_message == "OK")


def main():
    unittest.main()

if __name__ == '__main__':
    main()
