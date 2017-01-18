"""Python client for Sift Science's API.
See: https://siftscience.com/docs/references/events-api
"""

import json
import requests
import requests.auth
import sys
if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib

import sift
import sift.version

API_URL = 'https://api.siftscience.com'
API3_URL = 'https://api3.siftscience.com'
DECISION_SOURCES = ['MANUAL_REVIEW', 'AUTOMATED_RULE', 'CHARGEBACK']


class Client(object):

    def __init__(
            self,
            api_key=None,
            api_url=API_URL,
            timeout=2.0,
            account_id=None,
            version=sift.version.API_VERSION):
        """Initialize the client.

        Args:
            api_key: Your Sift Science API key associated with your customer
                account. You can obtain this from
                https://siftscience.com/console/developer/api-keys .

            api_url: Base URL, including scheme and host, for sending events.
                Defaults to 'https://api.siftscience.com'.

            timeout: Number of seconds to wait before failing request. Defaults
                to 2 seconds.

            account_id: The ID of your Sift Science account.  You can obtain
                this from https://siftscience.com/console/account/profile .

            version: The version of the Sift Science API to call.  Defaults to
                the latest version ('204').

        """
        if not isinstance(api_url, str) or len(api_url.strip()) == 0:
            raise ApiException("api_url must be a string")

        if api_key is None:
            api_key = sift.api_key

        if not isinstance(api_key, str) or len(api_key.strip()) == 0:
            raise ApiException("valid api_key is required")

        self.api_key = api_key
        self.url = api_url
        self.timeout = timeout
        self.account_id = account_id or sift.account_id
        self.version = version
        if sys.version_info[0] < 3:
            self.UNICODE_STRING = basestring
        else:
            self.UNICODE_STRING = str


    def track(
            self,
            event,
            properties,
            path=None,
            return_score=False,
            return_action=False,
            return_workflow_status=False,
            abuse_types=None,
            timeout=None,
            version=None):
        """Track an event and associated properties to the Sift Science client.
        This call is blocking.  Check out https://siftscience.com/resources/references/events-api
        for more information on what types of events you can send and fields you can add to the
        properties parameter.

        Args:
            event: The name of the event to send. This can either be a reserved
                event name such as "$transaction" or "$create_order" or a custom event
                name (that does not start with a $).

            properties: A dict of additional event-specific attributes to track.

            return_score: Whether the API response should include a score for this
                 user (the score will be calculated using this event).

            return_action: Whether the API response should include actions in the response. For
                 more information on how this works, please visit the tutorial at:
                 https://siftscience.com/resources/tutorials/formulas .

            return_workflow_status: Whether the API response should
                 include the status of any workflow run as a result of
                 the tracked event.

            abuse_types(optional): List of abuse types, specifying for which abuse types a score
                 should be returned (if scores were requested).  If not specified, a score will
                 be returned for every abuse_type to which you are subscribed.

            timeout(optional): Use a custom timeout (in seconds) for this call.

            version(optional): Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the track call succeeded, otherwise
            raises an ApiException.

        """
        if not isinstance(event, self.UNICODE_STRING) or len(event.strip()) == 0:
            raise ApiException("event must be a string")

        if not isinstance(properties, dict) or len(properties) == 0:
            raise ApiException("properties dictionary may not be empty")

        headers = {'Content-type': 'application/json',
                   'Accept': '*/*',
                   'User-Agent': self._user_agent()}

        if version is None:
            version = self.version

        if path is None:
            path = self._event_url(version)

        if timeout is None:
            timeout = self.timeout

        properties.update({'$api_key': self.api_key, '$type': event})
        params = {}

        if return_score:
            params['return_score'] = 'true'

        if return_action:
            params['return_action'] = 'true'

        if abuse_types:
            params['abuse_types'] = ','.join(abuse_types)

        if return_workflow_status:
            params['return_workflow_status'] = 'true'

        try:
            response = requests.post(
                path,
                data=json.dumps(properties),
                headers=headers,
                timeout=timeout,
                params=params)
            return Response(response)
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))


    def score(self, user_id, timeout=None, abuse_types=None, version=None):
        """Retrieves a user's fraud score from the Sift Science API.
        This call is blocking.  Check out https://siftscience.com/resources/references/score_api.html
        for more information on our Score response structure.

        Args:
            user_id:  A user's id. This id should be the same as the user_id used in
                event calls.

            timeout(optional): Use a custom timeout (in seconds) for this call.

            abuse_types(optional): List of abuse types, specifying for which abuse types a score
                 should be returned (if scores were requested).  If not specified, a score will
                 be returned for every abuse_type to which you are subscribed.

            version(optional): Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the score call succeeded, or raises
            an ApiException.
        """
        if not isinstance(user_id, self.UNICODE_STRING) or len(user_id.strip()) == 0:
            raise ApiException("user_id must be a string")

        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        headers = {'User-Agent': self._user_agent()}
        params = {'api_key': self.api_key}
        if abuse_types:
            params['abuse_types'] = ','.join(abuse_types)

        try:
            response = requests.get(
                self._score_url(user_id, version),
                headers=headers,
                timeout=timeout,
                params=params)
            return Response(response)
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))


    def label(self, user_id, properties, timeout=None, version=None):
        """Labels a user as either good or bad through the Sift Science API.
        This call is blocking.  Check out https://siftscience.com/resources/references/labels_api.html
        for more information on what fields to send in properties.

        Args:
            user_id:  A user's id. This id should be the same as the user_id used in
                event calls.

            properties: A dict of additional event-specific attributes to track.

            timeout(optional): Use a custom timeout (in seconds) for this call.

            version(optional): Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the label call succeeded, otherwise
            raises an ApiException.
        """
        if not isinstance(user_id, self.UNICODE_STRING) or len(user_id.strip()) == 0:
            raise ApiException("user_id must be a string")

        if version is None:
            version = self.version

        return self.track(
            '$label',
            properties,
            path=self._label_url(user_id, version),
            timeout=timeout,
            version=version)


    def unlabel(self, user_id, timeout=None, abuse_type=None, version=None):
        """unlabels a user through the Sift Science API.
        This call is blocking.  Check out https://siftscience.com/resources/references/labels_api.html
        for more information.

        Args:
            user_id:  A user's id. This id should be the same as the user_id used in
                event calls.

            timeout(optional): Use a custom timeout (in seconds) for this call.

            abuse_type(optional): The abuse type for which the user should be unlabeled.
                If omitted, the user is unlabeled for all abuse types.

            version(optional): Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the unlabel call succeeded, otherwise
            raises an ApiException.
        """
        if not isinstance(user_id, self.UNICODE_STRING) or len(user_id.strip()) == 0:
            raise ApiException("user_id must be a string")

        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        headers = {'User-Agent': self._user_agent()}
        params = {'api_key': self.api_key}
        if abuse_type:
            params['abuse_type'] = abuse_type

        try:

            response = requests.delete(
                self._label_url(user_id, version),
                headers=headers,
                timeout=timeout,
                params=params)
            return Response(response)

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))


    def get_workflow_status(self, run_id, timeout=None):
        """Gets the status of a workflow run.

        Args:
            run_id: The ID of a workflow run.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.

        """
        if not isinstance(run_id, self.UNICODE_STRING) or len(run_id.strip()) == 0:
            raise ApiException("run_id must be a string")

        if timeout is None:
            timeout = self.timeout

        try:
            return Response(requests.get(
                self._workflow_status_url(self.account_id, run_id),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))

    def get_decisions(self, entity_type, limit=None, start_from=None, abuse_types=None, timeout=None):
        """Get decisions available to customer

        Args:
            entity_type: only return decisions applicable to entity type {USER|ORDER}
            limit: number of query results (decisions) to return [optional, default: 100]
            start_from: result set offset for use in pagination [optional, default: 0]
            abuse_types: comma-separated list of abuse_types used to filter returned decisions (optional)

        Returns:
            A sift.client.Response object containing array of decisions if call succeeded
            Otherwise raises an ApiException
        """

        if timeout is None:
            timeout = self.timeout

        params = {}

        if not isinstance(entity_type, self.UNICODE_STRING) or len(entity_type.strip()) == 0 \
                or entity_type.lower() not in ['user', 'order']:
            raise ApiException("entity_type must be one of {user, order}")

        params['entity_type'] = entity_type

        if limit:
            params['limit'] = limit

        if start_from:
            params['from'] = start_from

        if abuse_types:
            params['abuse_types'] = abuse_types

        try:
            return Response(requests.get(self._get_decisions_url(self.account_id), params=params,
                                         auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                                         headers={'User-Agent': self._user_agent()}, timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))

    def apply_user_decision(self, user_id, properties, timeout=None):
        """Apply decision to user

        Args:
            user_id: id of user
            properties:
                decision_id: decision to apply to user
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                time: in millis when decision was applied
        Returns
            A sift.client.Response object if the call succeeded, else raises an ApiException
        """

        if timeout is None:
            timeout = self.timeout

        self._validate_apply_decision_request(properties, user_id)

        try:
            return Response(requests.post(
                self._user_decisions_url(self.account_id, user_id),
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))

    def apply_order_decision(self, user_id, order_id, properties, timeout=None):
        """Apply decision to order

        Args:
            user_id: id of user
            order_id: id of order
            properties:
                decision_id: decision to apply to user
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                description: free form text (optional)
                time: in millis when decision was applied (optional)
        Returns
            A sift.client.Response object if the call succeeded, else raises an ApiException
        """

        if timeout is None:
            timeout = self.timeout


        if order_id is None or not isinstance(order_id, self.UNICODE_STRING) or \
                        len(order_id.strip()) == 0:
            raise ApiException("order_id must be a string")

        self._validate_apply_decision_request(properties, user_id)

        try:
            return Response(requests.post(
                self._order_apply_decisions_url(self.account_id, user_id, order_id),
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))

    def _validate_apply_decision_request(self, properties, user_id):
        if not isinstance(user_id, self.UNICODE_STRING) or len(user_id.strip()) == 0:
            raise ApiException("user_id must be a string")

        if not isinstance(properties, dict) or len(properties) == 0:
            raise ApiException("properties dictionary may not be empty")

        source = properties.get('source')

        if not isinstance(source, self.UNICODE_STRING) or len(source.strip()) == 0 or source not in DECISION_SOURCES:
            raise ApiException("decision 'source' must be one of [%s]" % ", ".join(DECISION_SOURCES))

        properties.update({'source': source.upper()})

        if source == 'MANUAL_REVIEW' and \
                ('analyst' not in properties or len(properties.get('analyst')) == 0):
            raise ApiException("must provide 'analyst' for decision 'source':'MANUAL_REVIEW'")


    def get_user_decisions(self, user_id, timeout=None):
        """Gets the decisions for a user.

        Args:
            user_id: The ID of a user.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.

        """
        if not isinstance(user_id, self.UNICODE_STRING) or len(user_id.strip()) == 0:
            raise ApiException("user_id must be a string")

        if timeout is None:
            timeout = self.timeout

        try:
            return Response(requests.get(
                self._user_decisions_url(self.account_id, user_id),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))


    def get_order_decisions(self, order_id, timeout=None):
        """Gets the decisions for an order.

        Args:
            order_id: The ID of an order.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.

        """
        if not isinstance(order_id, self.UNICODE_STRING) or len(order_id.strip()) == 0:
            raise ApiException("order_id must be a string")

        if timeout is None:
            timeout = self.timeout

        try:
            return Response(requests.get(
                self._order_decisions_url(self.account_id, order_id),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e))


    def _user_agent(self):
        return 'SiftScience/v%s sift-python/%s' % (sift.version.API_VERSION, sift.version.VERSION)

    def _event_url(self, version):
        return self.url + '/v%s/events' % version

    def _score_url(self, user_id, version):
        return self.url + '/v%s/score/%s' % (version, urllib.quote(user_id))

    def _label_url(self, user_id, version):
        return self.url + '/v%s/users/%s/labels' % (version, urllib.quote(user_id))

    def _workflow_status_url(self, account_id, run_id):
        return API3_URL + '/v3/accounts/%s/workflows/runs/%s' % (account_id, run_id)

    def _get_decisions_url(self, account_id):
        return API3_URL + '/v3/accounts/%s/decisions' % (account_id)

    def _user_decisions_url(self, account_id, user_id):
        return API3_URL + '/v3/accounts/%s/users/%s/decisions' % (account_id, user_id)

    def _order_decisions_url(self, account_id, order_id):
        return API3_URL + '/v3/accounts/%s/orders/%s/decisions' % (account_id, order_id)

    def _order_apply_decisions_url(self, account_id, user_id, order_id):
        return API3_URL + '/v3/accounts/%s/users/%s/orders/%s/decisions' % (account_id, user_id, order_id)

class Response(object):

    HTTP_CODES_WITHOUT_BODY = [204, 304]

    def __init__(self, http_response):
        """
        Raises ApiException on invalid JSON in Response body or non-2XX HTTP
        status code.
        """
        # Set defaults.
        self.body = None
        self.request = None
        self.api_status = None
        self.api_error_message = None
        self.http_status_code = http_response.status_code
        self.url = http_response.url

        if (self.http_status_code not in self.HTTP_CODES_WITHOUT_BODY) and http_response.text:
            try:
                self.body = http_response.json()
                if 'status' in self.body:
                    self.api_status = self.body['status']
                if 'error_message' in self.body:
                    self.api_error_message = self.body['error_message']
                if 'request' in self.body.keys() and isinstance(self.body['request'], str):
                    self.request = json.loads(self.body['request'])
            except ValueError:
                not_json_warning = "Failed to parse json response from {}.  HTTP status code: {}.".format(self.url, self.http_status_code)
                raise ApiException(not_json_warning)
            finally:
                if (int(self.http_status_code) < 200 or int(self.http_status_code) >= 300):
                    non_2xx_warning = "{} returned non-2XX http status code {}".format(self.url, self.http_status_code)
                    if self.api_error_message:
                        non_2xx_warning += " with error message: {}".format(self.api_error_message)
                    raise ApiException(non_2xx_warning)

    def __str__(self):
        return ('{%s "http_status_code": %s}' %
                ('' if self.body is None else '"body": ' +
                 json.dumps(self.body) + ',', str(self.http_status_code)))

    def is_ok(self):

        if self.http_status_code in self.HTTP_CODES_WITHOUT_BODY:
            return 204 == self.http_status_code

        # NOTE: Responses from /v3/... endpoints do not contain an API status.
        if self.api_status:
            return self.api_status == 0

        return self.http_status_code == 200


class ApiException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
