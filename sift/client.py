"""Python client for Sift Science's REST API
(https://siftscience.com/docs/rest-api).
"""

import json
import logging
import traceback

import grequests


API_URL = 'https://api.siftscience.com/v203'
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
        self.pool = grequests.Pool(10)

    def track(self, event, properties):
        """Track an event and associated properties to the Sift Science client.

        Args:
            event: The name of the event to send. This can either be a reserved
                event name such as "$transaction" or "$label" or a custom event
                name (that does not start with a $).
            properties: A dict of additional event-specific attributes to track

            See: https://siftscience.com/docs/references/events-api

        Returns:
            A requests.Response object if the track call succeeded, otherwise
            a subclass of requests.exceptions.RequestException indicating the
            exception that occurred.
        """
        headers = { 'Content-type' : 'application/json', 'Accept' : '*/*' }
        properties.update({ '$api_key': self.api_key, '$type': event })

        def callback(response, **kwargs):
            if response.status_code != 200:
                error_message = str(json.loads(response.content)['error_message'])
                raise SiftAPIClientError(error_message)

        try:
            response = grequests.post(self.url+'/events', data=json.dumps(properties),
                    headers=headers, timeout=self.timeout, hooks={'response' : callback})
            # TODO(david): Wrap the response object in a class

            job = grequests.send(response, self.pool)

            return job

        except grequests.exceptions.RequestException as e:
            sift_logger.warn('Failed to track event: %s' % properties)
            sift_logger.warn(traceback.format_exception_only(type(e), e))

            return e

    def label(self, user_id, properties):
        '''Label a user to provide feedback to Sift Science and improve the
        machine learning model. This call is blocking.

        Args:
            user_id: The user's ID as string
            properties: a dictionary of label properties, including:
                $is_bad: a boolean value indicating if the user is bad. REQUIRED
                $reasons: a list of reasons why the user is considered bad. OPTIONAL
                $description: a string for free form description of theuser. OPTIONAL

            See: https://siftscience.com/docs/references/labels-api/

        Returns:
            A requests.Response object if the track call succeeded, otherwise
            a subclass of requests.exceptions.RequestException indicating the
            exception that occurred.
        '''

        headers = { 'Content-type': 'application/json', 'Accept' : '*/*' }
        properties.update({
            '$api_key': self.api_key,
        })

        label_url_format = self.url+'/users/%s/labels'

        if type(user_id) is str:
            label_endpoint = label_url_format % (user_id)
        else:
            raise SiftAPIClientError('User ID is not a string.')

        def callback(response, **kwargs):
            if response.status_code != 200:
                error_message = str(json.loads(response.content)['error_message'])
                raise SiftAPIClientError(error_message)

        try:
            response = grequests.post(label_endpoint, data=json.dumps(properties),
                    headers=headers, timeout=self.timeout)

            job = grequests.send(response, self.pool)

            return job

        except grequests.exceptions.RequestException as e:
            sift_logger.warn('Labeling user "%s" failed: %s' % (user, properties))
            sift_logger.warn(traceback.format_exception_only(type(e), e))

            return e

class SiftAPIClientError(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)