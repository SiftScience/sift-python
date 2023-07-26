"""Python client for Sift Science's API.
See: https://siftscience.com/docs/references/events-api
"""

import decimal
import json
import requests
import requests.auth
import sys

if sys.version_info[0] < 3:
    import six.moves.urllib as urllib

    _UNICODE_STRING = str
else:
    import urllib.parse

    _UNICODE_STRING = str

import sift
import sift.version

API_URL = 'https://api.siftscience.com'
API3_URL = 'https://api3.siftscience.com'
API_URL_VERIFICATION = 'https://api.sift.com/v1/verification/'

DECISION_SOURCES = ['MANUAL_REVIEW', 'AUTOMATED_RULE', 'CHARGEBACK']


def _quote_path(s):
    # by default, urllib.quote doesn't escape forward slash; pass the
    # optional arg to override this
    return urllib.parse.quote(s, '')


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return (str(o),)
        return super(DecimalEncoder, self).default(o)


class Client(object):

    def __init__(
            self,
            api_key=None,
            api_url=API_URL,
            timeout=2.0,
            account_id=None,
            version=sift.version.API_VERSION,
            session=None):
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
                the latest version ('205').

        """
        _assert_non_empty_unicode(api_url, 'api_url')

        if api_key is None:
            api_key = sift.api_key

        _assert_non_empty_unicode(api_key, 'api_key')

        self.session = session or requests.Session()
        self.api_key = api_key
        self.url = api_url
        self.timeout = timeout
        self.account_id = account_id or sift.account_id
        self.version = version

    def track(
            self,
            event,
            properties,
            path=None,
            return_score=False,
            return_action=False,
            return_workflow_status=False,
            return_route_info=False,
            force_workflow_run=False,
            abuse_types=None,
            timeout=None,
            version=None,
            include_score_percentiles=False):
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

            return_route_info: Whether to get the route information from the Workflow Decision.
                This parameter must be used with the return_workflow_status query parameter.

            force_workflow_run: TODO:(rlong) Add after Rishabh adds documentation.

            abuse_types(optional): List of abuse types, specifying for which abuse types a score
                 should be returned (if scores were requested).  If not specified, a score will
                 be returned for every abuse_type to which you are subscribed.

            timeout(optional): Use a custom timeout (in seconds) for this call.

            version(optional): Use a different version of the Sift Science API for this call.

            include_score_percentiles(optional) : Whether to add new parameter in the query parameter.
                if include_score_percentiles is true then add a new parameter called fields in the query parameter

        Returns:
            A sift.client.Response object if the track call succeeded, otherwise
            raises an ApiException.

        """
        _assert_non_empty_unicode(event, 'event')
        _assert_non_empty_dict(properties, 'properties')

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

        if return_route_info:
            params['return_route_info'] = 'true'

        if force_workflow_run:
            params['force_workflow_run'] = 'true'

        if include_score_percentiles:
            field_types = ['SCORE_PERCENTILES']
            params['fields'] = ','.join(field_types)
        try:
            response = self.session.post(
                path,
                data=json.dumps(properties, cls=DecimalEncoder),
                headers=headers,
                timeout=timeout,
                params=params)
            return Response(response)
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), path)

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
        _assert_non_empty_unicode(user_id, 'user_id')

        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        headers = {'User-Agent': self._user_agent()}
        params = {'api_key': self.api_key}
        if abuse_types:
            params['abuse_types'] = ','.join(abuse_types)

        url = self._score_url(user_id, version)

        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=timeout,
                params=params)
            return Response(response)
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def get_user_score(self, user_id, timeout=None, abuse_types=None):
        """Fetches the latest score(s) computed for the specified user and abuse types from the Sift Science API.
        As opposed to client.score() and client.rescore_user(), this *does not* compute a new score for the user; it
        simply fetches the latest score(s) which have computed. These scores may be arbitrarily old.

        This call is blocking. See https://siftscience.com/developers/docs/python/score-api/get-score for more details.

        Args:
            user_id:  A user's id. This id should be the same as the user_id used in
                event calls.

            timeout(optional): Use a custom timeout (in seconds) for this call.

            abuse_types(optional): List of abuse types, specifying for which abuse types a score
                 should be returned (if scores were requested).  If not specified, a score will
                 be returned for every abuse_type to which you are subscribed.

        Returns:
            A sift.client.Response object if the score call succeeded, or raises
            an ApiException.
        """
        _assert_non_empty_unicode(user_id, 'user_id')

        if timeout is None:
            timeout = self.timeout

        url = self._user_score_url(user_id, self.version)
        headers = {'User-Agent': self._user_agent()}
        params = {'api_key': self.api_key}
        if abuse_types:
            params['abuse_types'] = ','.join(abuse_types)

        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=timeout,
                params=params)
            return Response(response)
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def rescore_user(self, user_id, timeout=None, abuse_types=None):
        """Rescores the specified user for the specified abuse types and returns the resulting score(s).
        This call is blocking. See https://siftscience.com/developers/docs/python/score-api/rescore for more details.

        Args:
            user_id:  A user's id. This id should be the same as the user_id used in
                event calls.

            timeout(optional): Use a custom timeout (in seconds) for this call.

            abuse_types(optional): List of abuse types, specifying for which abuse types a score
                 should be returned (if scores were requested).  If not specified, a score will
                 be returned for every abuse_type to which you are subscribed.

        Returns:
            A sift.client.Response object if the score call succeeded, or raises
            an ApiException.
        """
        _assert_non_empty_unicode(user_id, 'user_id')

        if timeout is None:
            timeout = self.timeout

        url = self._user_score_url(user_id, self.version)
        headers = {'User-Agent': self._user_agent()}
        params = {'api_key': self.api_key}
        if abuse_types:
            params['abuse_types'] = ','.join(abuse_types)

        try:
            response = self.session.post(
                url,
                headers=headers,
                timeout=timeout,
                params=params)
            return Response(response)
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

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
        _assert_non_empty_unicode(user_id, 'user_id')

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
        _assert_non_empty_unicode(user_id, 'user_id')

        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        url = self._label_url(user_id, version)
        headers = {'User-Agent': self._user_agent()}
        params = {'api_key': self.api_key}
        if abuse_type:
            params['abuse_type'] = abuse_type

        try:
            response = self.session.delete(
                url,
                headers=headers,
                timeout=timeout,
                params=params)
            return Response(response)

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def get_workflow_status(self, run_id, timeout=None):
        """Gets the status of a workflow run.

        Args:
            run_id: The ID of a workflow run.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.

        """
        _assert_non_empty_unicode(run_id, 'run_id')

        url = self._workflow_status_url(self.account_id, run_id)
        if timeout is None:
            timeout = self.timeout

        try:
            return Response(self.session.get(
                url,
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def get_decisions(self, entity_type, limit=None, start_from=None, abuse_types=None, timeout=None):
        """Get decisions available to customer

        Args:
            entity_type: only return decisions applicable to entity type {USER|ORDER|SESSION|CONTENT}
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

        _assert_non_empty_unicode(entity_type, 'entity_type')
        if entity_type.lower() not in ['user', 'order', 'session', 'content']:
            raise ValueError("entity_type must be one of {user, order, session, content}")

        params['entity_type'] = entity_type

        if limit:
            params['limit'] = limit

        if start_from:
            params['from'] = start_from

        if abuse_types:
            params['abuse_types'] = abuse_types

        url = self._get_decisions_url(self.account_id)

        try:
            return Response(self.session.get(url, params=params,
                                             auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                                             headers={'User-Agent': self._user_agent()}, timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

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
        url = self._user_decisions_url(self.account_id, user_id)
        try:
            return Response(self.session.post(
                url,
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def apply_order_decision(self, user_id, order_id, properties, timeout=None):
        """Apply decision to order

        Args:
            user_id: id of user
            order_id: id of order
            properties:
                decision_id: decision to apply to order
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                description: free form text (optional)
                time: in millis when decision was applied (optional)
        Returns
            A sift.client.Response object if the call succeeded, else raises an ApiException
        """

        if timeout is None:
            timeout = self.timeout

        _assert_non_empty_unicode(user_id, 'user_id')
        _assert_non_empty_unicode(order_id, 'order_id')

        self._validate_apply_decision_request(properties, user_id)

        url = self._order_apply_decisions_url(self.account_id, user_id, order_id)
        try:
            return Response(self.session.post(
                url,
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def _validate_apply_decision_request(self, properties, user_id):
        _assert_non_empty_unicode(user_id, 'user_id')

        if not isinstance(properties, dict):
            raise TypeError("properties must be a dict")
        elif not properties:
            raise ValueError("properties dictionary may not be empty")

        source = properties.get('source')

        _assert_non_empty_unicode(source, 'source', error_cls=ValueError)
        if source not in DECISION_SOURCES:
            raise ValueError("decision 'source' must be one of [{0}]".format(", ".join(DECISION_SOURCES)))

        properties.update({'source': source.upper()})

        if source == 'MANUAL_REVIEW' and not properties.get('analyst', None):
            raise ValueError("must provide 'analyst' for decision 'source': 'MANUAL_REVIEW'")

    def get_user_decisions(self, user_id, timeout=None):
        """Gets the decisions for a user.

        Args:
            user_id: The ID of a user.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.

        """
        _assert_non_empty_unicode(user_id, 'user_id')

        if timeout is None:
            timeout = self.timeout

        url = self._user_decisions_url(self.account_id, user_id)

        try:
            return Response(self.session.get(
                url,
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def get_order_decisions(self, order_id, timeout=None):
        """Gets the decisions for an order.

        Args:
            order_id: The ID of an order.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.

        """
        _assert_non_empty_unicode(order_id, 'order_id')

        if timeout is None:
            timeout = self.timeout

        url = self._order_decisions_url(self.account_id, order_id)

        try:
            return Response(self.session.get(
                url,
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def get_content_decisions(self, user_id, content_id, timeout=None):
        """Gets the decisions for a piece of content.

        Args:
            user_id: The ID of the owner of the content.
            content_id: The ID of a piece of content.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.

        """
        _assert_non_empty_unicode(content_id, 'content_id')
        _assert_non_empty_unicode(user_id, 'user_id')

        if timeout is None:
            timeout = self.timeout

        url = self._content_decisions_url(self.account_id, user_id, content_id)

        try:
            return Response(self.session.get(
                url,
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def get_session_decisions(self, user_id, session_id, timeout=None):
        """Gets the decisions for a user's session.

        Args:
            user_id: The ID of a user.
            session_id: The ID of a session.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.

        """
        _assert_non_empty_unicode(user_id, 'user_id')
        _assert_non_empty_unicode(session_id, 'session_id')

        if timeout is None:
            timeout = self.timeout

        url = self._session_decisions_url(self.account_id, user_id, session_id)

        try:
            return Response(self.session.get(
                url,
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def apply_session_decision(self, user_id, session_id, properties, timeout=None):
        """Apply decision to session

        Args:
            user_id: id of user
            session_id: id of session
            properties:
                decision_id: decision to apply to session
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                description: free form text (optional)
                time: in millis when decision was applied (optional)
        Returns
            A sift.client.Response object if the call succeeded, else raises an ApiException
        """

        if timeout is None:
            timeout = self.timeout

            _assert_non_empty_unicode(session_id, 'session_id')

        self._validate_apply_decision_request(properties, user_id)

        url = self._session_apply_decisions_url(self.account_id, user_id, session_id)

        try:
            return Response(self.session.post(
                url,
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def apply_content_decision(self, user_id, content_id, properties, timeout=None):
        """Apply decision to content

        Args:
            user_id: id of user
            content_id: id of content
            properties:
                decision_id: decision to apply to session
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                description: free form text (optional)
                time: in millis when decision was applied (optional)
        Returns
            A sift.client.Response object if the call succeeded, else raises an ApiException
        """

        if timeout is None:
            timeout = self.timeout

        _assert_non_empty_unicode(content_id, 'content_id')

        self._validate_apply_decision_request(properties, user_id)

        url = self._content_apply_decisions_url(self.account_id, user_id, content_id)

        try:
            return Response(self.session.post(
                url,
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def create_psp_merchant_profile(self, properties, timeout=None):
        """Create a new PSP Merchant profile
        Args:
            properties: A dict of merchant profile data.
        Returns
            A sift.client.Response object if the call succeeded, else raises an ApiException
        """

        if timeout is None:
            timeout = self.timeout

        url = self._psp_merchant_url(self.account_id)

        try:
            return Response(self.session.post(
                url,
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def update_psp_merchant_profile(self, merchant_id, properties, timeout=None):
        """Update already existing PSP Merchant profile
        Args:
            merchant_id: id of merchant
            properties: A dict of merchant profile data.
        Returns
            A sift.client.Response object if the call succeeded, else raises an ApiException
        """

        if timeout is None:
            timeout = self.timeout

        url = self._psp_merchant_id_url(self.account_id, merchant_id)
        try:
            return Response(self.session.put(
                url,
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def get_psp_merchant_profiles(self, batch_token=None, batch_size=None, timeout=None):
        """Gets all PSP merchant profiles.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.
        """

        if timeout is None:
            timeout = self.timeout

        url = self._psp_merchant_url(self.account_id)
        params = {}

        if batch_size:
            params['batch_size'] = batch_size

        if batch_token:
            params['batch_token'] = batch_token
        try:
            return Response(self.session.get(
                url,
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                params=params,
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def get_a_psp_merchant_profile(self, merchant_id, timeout=None):
        """Gets a PSP merchant profile using merchant id.

        Returns:
            A sift.client.Response object if the call succeeded.
            Otherwise, raises an ApiException.
        """

        if timeout is None:
            timeout = self.timeout

        url = self._psp_merchant_id_url(self.account_id, merchant_id)

        try:
            return Response(self.session.get(
                url,
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'User-Agent': self._user_agent()},
                timeout=timeout))
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

    def verification_send(self, properties, timeout=None,  version=None):
        """The send call triggers the generation of a OTP code that is stored by Sift and email/sms the code to the user.
        This call is blocking. Check out https://sift.com/developers/docs/python/verification-api/send
        for more information on our send response structure.

        Args:

            properties: 

                $user_id: User ID of user being verified, e.g. johndoe123.
                $send_to: The phone / email to send the OTP to.
                $verification_type: The channel used for verification. Should be either $email or $sms.
                $brand_name(optional): Name of the brand of product or service the user interacts with.
                $language(optional): Language of the content of the web site.
                $site_country(optional): Country of the content of the site.
                $event: 
                    $session_id:  The session being verified. See $verification in the Sift Events API documentation.
                    $verified_event: The type of the reserved event being verified.
                    $reason(optional): The trigger for the verification. See $verification in the Sift Events API documentation.
                    $ip(optional): The user's IP address.
                    $browser:
                        $user_agent: The user agent of the browser that is verifying. Represented by the $browser object.
                                     Use this field if the client is a browser.


            timeout(optional): Use a custom timeout (in seconds) for this call.

            version(optional): Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the send call succeeded, or raises an ApiException.
        """

        if timeout is None:
            timeout = self.timeout

        self._validate_send_request(properties)

        url = self._verification_send_url()

        try:
            return Response(self.session.post(
                url,
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)  

    def _validate_send_request(self, properties):
        """ This method is used to validate arguments passed to the send method. """

        if not isinstance(properties, dict):
            raise TypeError("properties must be a dict")
        elif not properties:
            raise ValueError("properties dictionary may not be empty")

        user_id = properties.get('$user_id')
        _assert_non_empty_unicode(user_id, 'user_id', error_cls=ValueError)

        send_to = properties.get('$send_to')
        _assert_non_empty_unicode(send_to, 'send_to', error_cls=ValueError)

        verification_type = properties.get('$verification_type')
        _assert_non_empty_unicode(
            verification_type, 'verification_type', error_cls=ValueError)

        event = properties.get('$event')
        if not isinstance(event, dict):
            raise TypeError("$event must be a dict")
        elif not event:
            raise ValueError("$event dictionary may not be empty")

        session_id = event.get('$session_id')
        _assert_non_empty_unicode(
            session_id, 'session_id', error_cls=ValueError)
    
    def verification_resend(self, properties, timeout=None,  version=None):
        """A user can ask for a new OTP (one-time password) if they haven't received the previous one,
        or in case the previous OTP expired.
        This call is blocking. Check out https://sift.com/developers/docs/python/verification-api/resend
        for more information on our send response structure.

        Args:

            properties: 

                $user_id: User ID of user being verified, e.g. johndoe123.
                $verified_event(optional): This will be the event type that triggered the verification.
                $verified_entity_id(optional): The ID of the entity impacted by the event being verified.

            timeout(optional): Use a custom timeout (in seconds) for this call.

            version(optional): Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the send call succeeded, or raises an ApiException.
        """

        if timeout is None:
            timeout = self.timeout

        self._validate_resend_request(properties)

        url = self._verification_resend_url()

        try:
            return Response(self.session.post(
                url,
                data=json.dumps(properties),
                auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                headers={'Content-type': 'application/json',
                         'Accept': '*/*',
                         'User-Agent': self._user_agent()},
                timeout=timeout))

        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)  

    def _validate_resend_request(self, properties):
        """ This method is used to validate arguments passed to the send method. """

        if not isinstance(properties, dict):
            raise TypeError("properties must be a dict")
        elif not properties:
            raise ValueError("properties dictionary may not be empty")

        user_id = properties.get('$user_id')
        _assert_non_empty_unicode(user_id, 'user_id', error_cls=ValueError)
    
    def verification_check(self, properties, timeout=None,  version=None):
            """The verification_check call is used for checking the OTP provided by the end user to Sift. 
            Sift then compares the OTP, checks rate limits and responds with a decision whether the user should be able to proceed or not.
            This call is blocking. Check out https://sift.com/developers/docs/python/verification-api/check
            for more information on our check response structure.

            Args:

                properties:
                    $user_id: User ID of user being verified, e.g. johndoe123.
                    $code: The code the user sent to the customer for validation..
                    $verified_event(optional): This will be the event type that triggered the verification. 
                    $verified_entity_id(optional): The ID of the entity impacted by the event being verified.

                timeout(optional): Use a custom timeout (in seconds) for this call.
                version(optional): Use a different version of the Sift Science API for this call.

            Returns:
                A sift.client.Response object if the check call succeeded, or raises
                an ApiException.
            """
            if timeout is None:
                timeout = self.timeout

            self._validate_check_request(properties)

            url = self._verification_check_url()

            try:
                return Response(self.session.post(
                    url,
                    data=json.dumps(properties),
                    auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                    headers={'Content-type': 'application/json',
                            'Accept': '*/*',
                            'User-Agent': self._user_agent()},
                    timeout=timeout))

            except requests.exceptions.RequestException as e:
                raise ApiException(str(e), url)

    def _validate_check_request(self, properties):
        """ This method is used to validate arguments passed to the check method. """

        if not isinstance(properties, dict):
            raise TypeError("properties must be a dict")
        elif not properties:
            raise ValueError("properties dictionary may not be empty")

        user_id = properties.get('$user_id')
        _assert_non_empty_unicode(user_id, 'user_id', error_cls=ValueError)

        otp_code = properties.get('$code')
        if otp_code is None:
            raise ValueError("code is required")
  
    def _user_agent(self):
        return 'SiftScience/v%s sift-python/%s' % (sift.version.API_VERSION, sift.version.VERSION)

    def _event_url(self, version):
        return self.url + '/v%s/events' % version

    def _score_url(self, user_id, version):
        return self.url + '/v%s/score/%s' % (version, _quote_path(user_id))

    def _user_score_url(self, user_id, version):
        return self.url + '/v%s/users/%s/score' % (version, urllib.parse.quote(user_id))

    def _label_url(self, user_id, version):
        return self.url + '/v%s/users/%s/labels' % (version, _quote_path(user_id))

    def _workflow_status_url(self, account_id, run_id):
        return (API3_URL + '/v3/accounts/%s/workflows/runs/%s' %
                (_quote_path(account_id), _quote_path(run_id)))

    def _get_decisions_url(self, account_id):
        return API3_URL + '/v3/accounts/%s/decisions' % (_quote_path(account_id),)

    def _user_decisions_url(self, account_id, user_id):
        return (API3_URL + '/v3/accounts/%s/users/%s/decisions' %
                (_quote_path(account_id), _quote_path(user_id)))

    def _order_decisions_url(self, account_id, order_id):
        return (API3_URL + '/v3/accounts/%s/orders/%s/decisions' %
                (_quote_path(account_id), _quote_path(order_id)))

    def _session_decisions_url(self, account_id, user_id, session_id):
        return (API3_URL + '/v3/accounts/%s/users/%s/sessions/%s/decisions' %
                (_quote_path(account_id), _quote_path(user_id), _quote_path(session_id)))

    def _content_decisions_url(self, account_id, user_id, content_id):
        return (API3_URL + '/v3/accounts/%s/users/%s/content/%s/decisions' %
                (_quote_path(account_id), _quote_path(user_id), _quote_path(content_id)))

    def _order_apply_decisions_url(self, account_id, user_id, order_id):
        return (API3_URL + '/v3/accounts/%s/users/%s/orders/%s/decisions' %
                (_quote_path(account_id), _quote_path(user_id), _quote_path(order_id)))

    def _session_apply_decisions_url(self, account_id, user_id, session_id):
        return (API3_URL + '/v3/accounts/%s/users/%s/sessions/%s/decisions' %
                (_quote_path(account_id), _quote_path(user_id), _quote_path(session_id)))

    def _content_apply_decisions_url(self, account_id, user_id, content_id):
        return (API3_URL + '/v3/accounts/%s/users/%s/content/%s/decisions' %
                (_quote_path(account_id), _quote_path(user_id), _quote_path(content_id)))

    def _psp_merchant_url(self, account_id):
        return (self.url + '/v3/accounts/%s/psp_management/merchants' %
                (_quote_path(account_id)))

    def _psp_merchant_id_url(self, account_id, merchant_id):
        return (self.url + '/v3/accounts/%s/psp_management/merchants/%s' %
                (_quote_path(account_id), _quote_path(merchant_id)))

    def _verification_send_url(self):
        return (API_URL_VERIFICATION + 'send')
    
    def _verification_resend_url(self):
        return (API_URL_VERIFICATION + 'resend')
    
    def _verification_check_url(self):
        return (API_URL_VERIFICATION + 'check')

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
                if 'request' in list(self.body.keys()) and isinstance(self.body['request'], str):
                    self.request = json.loads(self.body['request'])
            except ValueError:
                raise ApiException(
                    'Failed to parse json response from {0}'.format(self.url),
                    url=self.url,
                    http_status_code=self.http_status_code,
                    body=self.body,
                    api_status=self.api_status,
                    api_error_message=self.api_error_message,
                    request=self.request)
            finally:
                if int(self.http_status_code) < 200 or int(self.http_status_code) >= 300:
                    raise ApiException(
                        '{0} returned non-2XX http status code {1}'.format(self.url, self.http_status_code),
                        url=self.url,
                        http_status_code=self.http_status_code,
                        body=self.body,
                        api_status=self.api_status,
                        api_error_message=self.api_error_message,
                        request=self.request)

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
    def __init__(self, message, url, http_status_code=None, body=None, api_status=None,
                 api_error_message=None, request=None):
        Exception.__init__(self, message)

        self.url = url
        self.http_status_code = http_status_code
        self.body = body
        self.api_status = api_status
        self.api_error_message = api_error_message
        self.request = request


def _assert_non_empty_unicode(val, name, error_cls=None):
    error = False
    if not isinstance(val, _UNICODE_STRING):
        error_cls = error_cls or TypeError
        error = True
    elif not val:
        error_cls = error_cls or ValueError
        error = True

    if error:
        raise error_cls('{0} must be a non-empty string'.format(name))


def _assert_non_empty_dict(val, name):
    if not isinstance(val, dict):
        raise TypeError('{0} must be a non-empty dict'.format(name))
    elif not val:
        raise ValueError('{0} must be a non-empty dict'.format(name))
