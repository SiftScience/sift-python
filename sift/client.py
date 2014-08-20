"""Python client for Sift Science's API.
See: https://siftscience.com/docs/references/events-api
"""

import json
import logging
import requests
import traceback
import sys

import sift
from . import version

API_URL = 'https://api.siftscience.com'
sift_logger = logging.getLogger('sift_client')

class Client(object):
    def __init__(self, api_key = None, api_url=API_URL, timeout=2.0):
        """Initialize the client.

        Args:
            api_key: Your Sift Science API key associated with your customer
                account. You can obtain this from
                https://siftscience.com/quickstart
            api_url: The URL to send events to.
            timeout: Number of seconds to wait before failing request. Defaults
                to 2 seconds.
        """
        if not isinstance(api_url, str) or len(api_url.strip()) == 0:
            raise RuntimeError("api_url must be a string")

        if api_key is None:
          api_key = sift.api_key

        if not isinstance(api_key, str) or len(api_key.strip()) == 0:
            raise RuntimeError("valid api_key is required")

        self.api_key = api_key
        self.url = api_url + '/v%s' % version.API_VERSION
        self.timeout = timeout
        if sys.version_info.major < 3:
          self.UNICODE_STRING = basestring
        else:
          self.UNICODE_STRING = str

    def user_agent(self):
        return 'SiftScience/v%s sift-python/%s' % (version.API_VERSION, version.VERSION)

    def event_url(self):
        return self.url + '/events'

    def score_url(self, user_id):
        return self.url + '/score/%s' % user_id

    def label_url(self, user_id):
        return self.url + '/users/%s/labels' % user_id

    def track(self, event, properties, path=None, return_score=False):
        """Track an event and associated properties to the Sift Science client.
        This call is blocking.

        Args:
            event: The name of the event to send. This can either be a reserved
                event name such as "$transaction" or "$create_order" or a custom event
                name (that does not start with a $).
            properties: A dict of additional event-specific attributes to track
            return_score: Whether the API response should include a score for this 
                 user (the score will be calculated using this event)
        Returns:
            A requests.Response object if the track call succeeded, otherwise
            a subclass of requests.exceptions.RequestException indicating the
            exception that occurred.
        """
        if not isinstance(event, self.UNICODE_STRING) or len(event.strip()) == 0:
            raise RuntimeError("event must be a string")

        if not isinstance(properties, dict) or len(properties) == 0:
            raise RuntimeError("properties dictionary may not be empty")

        headers = { 'Content-type' : 'application/json',
                    'Accept' : '*/*',
                    'User-Agent' : self.user_agent() }

        if path is None:
          path = self.event_url()
        properties.update({ '$api_key': self.api_key, '$type': event })
        params = {}
        if return_score:
          params.update({ 'return_score' : return_score })
        try:
            response = requests.post(path, data=json.dumps(properties),
                    headers=headers, timeout=self.timeout, params=params)
            return Response(response)
        except requests.exceptions.RequestException as e:
            sift_logger.warn('Failed to track event: %s' % properties)
            sift_logger.warn(traceback.format_exception_only(type(e), e))

            return e

    def score(self, user_id):
        """Retrieves a user's fraud score from the Sift Science API.
        This call is blocking.

        Args:
            user_id:  A user's id. This id should be the same as the user_id used in
                event calls.
        Returns:
            A requests.Response object if the score call succeeded, otherwise
            a subclass of requests.exceptions.RequestException indicating the
            exception that occurred.
        """
        if not isinstance(user_id, self.UNICODE_STRING) or len(user_id.strip()) == 0:
            raise RuntimeError("user_id must be a string")

        headers = { 'User-Agent' : self.user_agent() }
        params = { 'api_key': self.api_key }

        try:
            response = requests.get(self.score_url(user_id),
                    headers=headers, timeout=self.timeout, params=params)
            return Response(response)
        except requests.exceptions.RequestException as e:
            sift_logger.warn('Failed to track event: %s' % properties)
            sift_logger.warn(traceback.format_exception_only(type(e), e))

            return e

    def label(self, user_id, properties):
        """Labels a user as either good or bad through the Sift Science API.
        This call is blocking.

        Args:
            user_id:  A user's id. This id should be the same as the user_id used in
                event calls.
            properties: A dict of additional event-specific attributes to track
        Returns:
            A requests.Response object if the label call succeeded, otherwise
            a subclass of requests.exceptions.RequestException indicating the
            exception that occurred.
        """
        if not isinstance(user_id, self.UNICODE_STRING) or len(user_id.strip()) == 0:
            raise RuntimeError("user_id must be a string")

        return self.track('$label', properties, self.label_url(user_id))

class Response(object):
    def __init__(self, http_response):
        self.body = http_response.json()
        self.http_status_code = http_response.status_code
        self.api_status = self.body['status']
        self.api_error_message = self.body['error_message']
        if 'request' in self.body.keys() and isinstance(self.body['request'], str):
            self.request = json.loads(self.body['request'])
        else:
            self.request = None

    def __str__(self):
        return ('{"body": %s, "http_status_code": %s}' %
                (json.dumps(self.body), str(self.http_status_code)))

    def is_ok(self):
        return self.api_status == 0
