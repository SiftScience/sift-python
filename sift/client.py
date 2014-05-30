"""Python client for Sift Science's API.
See: https://siftscience.com/docs/references/events-api
"""

import json
import logging
import requests
import traceback

from sift import version

API_URL = 'https://api.siftscience.com/v%s/events' % version.API_VERSION
sift_logger = logging.getLogger('sift_client')

class Client(object):
    def __init__(self, api_key, api_url=API_URL, timeout=2.0):
        """Initialize the client.

        Args:
            api_key: Your Sift Science API key associated with your customer
                account. You can obtain this from
                https://siftscience.com/quickstart
            api_url: The URL to send events to.
            timeout: Number of seconds to wait before failing request. Defaults
                to 2 seconds.
        """
        self.api_key = api_key
        self.url = api_url
        self.timeout = timeout

    def user_agent(self):
        return 'SiftScience/v%s sift-python/%s' % (version.API_VERSION, version.VERSION)

    def track(self, event, properties, return_score=False):
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
        headers = { 'Content-type' : 'application/json',
                    'Accept' : '*/*',
                    'User-Agent' : self.user_agent() }

        properties.update({ '$api_key': self.api_key, '$type': event })
        if return_score:
          params = { 'return_score' : return_score }
        try:
            response = requests.post(self.url, data=json.dumps(properties),
                    headers=headers, timeout=self.timeout, params=params)
            # TODO(david): Wrap the response object in a class
            return response
        except requests.exceptions.RequestException as e:
            sift_logger.warn('Failed to track event: %s' % properties)
            sift_logger.warn(traceback.format_exception_only(type(e), e))

            return e
