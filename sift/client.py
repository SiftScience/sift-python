"""Python client for Sift Science's API.
See: https://developers.sift.com/docs/python/events-api/
"""

from __future__ import annotations

import json
import sys
import typing as t
from collections.abc import Mapping, Sequence

import requests
from requests.auth import HTTPBasicAuth

import sift
from sift.constants import API_URL, DECISION_SOURCES
from sift.exceptions import ApiException
from sift.utils import DecimalEncoder, quote_path as _q
from sift.version import API_VERSION, VERSION


def _assert_non_empty_str(
    val: object,
    name: str,
    error_cls: type[Exception] | None = None,
) -> None:
    error = f"{name} must be a non-empty string"

    if not isinstance(val, str):
        error_cls = error_cls or TypeError
        raise error_cls(error)

    if not val:
        error_cls = error_cls or ValueError
        raise error_cls(error)


def _assert_non_empty_dict(val: object, name: str) -> None:
    error = f"{name} must be a non-empty mapping (dict)"

    if not isinstance(val, Mapping):
        raise TypeError(error)

    if not val:
        raise ValueError(error)


class Response:
    HTTP_CODES_WITHOUT_BODY = (204, 304)

    def __init__(self, http_response: requests.Response) -> None:
        """
        Raises ApiException on invalid JSON in Response body or non-2XX HTTP
        status code.
        """

        self.url: str = http_response.url
        self.http_status_code: int = http_response.status_code
        self.api_status: int | None = None
        self.api_error_message: str | None = None
        self.body: dict[str, t.Any] | None = None
        self.request: dict[str, t.Any] | None = None

        if (
            self.http_status_code not in self.HTTP_CODES_WITHOUT_BODY
        ) and http_response.text:
            try:
                self.body = http_response.json()

                if "status" in self.body:
                    self.api_status = self.body["status"]

                if "error_message" in self.body:
                    self.api_error_message = self.body["error_message"]

                if isinstance(self.body.get("request"), str):
                    self.request = json.loads(self.body["request"])
            except ValueError:
                raise ApiException(
                    f"Failed to parse json response from {self.url}",
                    url=self.url,
                    http_status_code=self.http_status_code,
                    body=self.body,
                    api_status=self.api_status,
                    api_error_message=self.api_error_message,
                    request=self.request,
                )
            finally:
                if not 200 <= self.http_status_code < 300:
                    raise ApiException(
                        f"{self.url} returned non-2XX http status code {self.http_status_code}",
                        url=self.url,
                        http_status_code=self.http_status_code,
                        body=self.body,
                        api_status=self.api_status,
                        api_error_message=self.api_error_message,
                        request=self.request,
                    )

    def __str__(self) -> str:
        body = (
            f'"body": {json.dumps(self.body)}, '
            if self.body is not None
            else ""
        )

        return f'{body}"http_status_code": {self.http_status_code}'

    def is_ok(self) -> bool:
        return self.api_status == 0 or self.http_status_code in (200, 204)


class Client:
    api_key: str
    account_id: str

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str = API_URL,
        timeout: float | tuple[float, float] = 2,
        account_id: str | None = None,
        version: str = API_VERSION,
        session: requests.Session | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            api_key:
                The Sift Science API key associated with your account. You can
                obtain it from https://console.sift.com/developer/api-keys

            api_url (optional):
                Base URL, including scheme and host, for sending events.
                Defaults to 'https://api.sift.com'.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.
                Defaults to 2 seconds.

            account_id (optional):
                The ID of your Sift Science account. You can obtain
                it from https://developers.sift.com/console/account/profile

            version (optional):
                The version of the Sift Science API to call.
                Defaults to the latest version.

            session (optional):
                requests.Session object
                https://requests.readthedocs.io/en/latest/user/advanced/#session-objects
        """
        _assert_non_empty_str(api_url, "api_url")

        if api_key is None:
            api_key = sift.api_key

        _assert_non_empty_str(api_key, "api_key")

        self.session = session or requests.Session()
        self.api_key = t.cast(str, api_key)
        self.url = api_url
        self.timeout = timeout
        self.account_id = t.cast(str, account_id or sift.account_id)
        self.version = version

    @staticmethod
    def _get_fields_param(
        include_score_percentiles: bool,
        include_warnings: bool,
    ) -> list[str]:
        return [
            field
            for include, field in (
                (include_score_percentiles, "SCORE_PERCENTILES"),
                (include_warnings, "WARNINGS"),
            )
            if include
        ]

    @property
    def _auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.api_key, "")

    def _user_agent(self, version: str | None = None) -> str:
        return (
            f"SiftScience/v{version or self.version} "
            f"sift-python/{VERSION} "
            f"Python/{sys.version.split(' ')[0]}"
        )

    def _default_headers(self, version: str | None = None) -> dict[str, str]:
        return {
            "User-Agent": self._user_agent(version),
        }

    def _post_headers(self, version: str | None = None) -> dict[str, str]:
        return {
            **self._default_headers(version),
            "Content-type": "application/json",
            "Accept": "*/*",
        }

    def _api_url(self, version: str, endpoint: str) -> str:
        return f"{self.url}/{version}{endpoint}"

    def _v1_api(self, endpoint: str) -> str:
        return self._api_url("v1", endpoint)

    def _v3_api(self, endpoint: str) -> str:
        return self._api_url("v3", endpoint)

    def _versioned_api(self, version: str, endpoint: str) -> str:
        return self._api_url(f"v{version}", endpoint)

    def _events_url(self, version: str) -> str:
        return self._versioned_api(version, "/events")

    def _score_url(self, user_id: str, version: str) -> str:
        return self._versioned_api(version, f"/score/{_q(user_id)}")

    def _user_score_url(self, user_id: str, version: str) -> str:
        return self._versioned_api(version, f"/users/{_q(user_id)}/score")

    def _labels_url(self, user_id: str, version: str) -> str:
        return self._versioned_api(version, f"/users/{_q(user_id)}/labels")

    def _workflow_status_url(self, account_id: str, run_id: str) -> str:
        return self._v3_api(
            f"/accounts/{_q(account_id)}/workflows/runs/{_q(run_id)}"
        )

    def _decisions_url(self, account_id: str) -> str:
        return self._v3_api(f"/accounts/{_q(account_id)}/decisions")

    def _order_decisions_url(self, account_id: str, order_id: str) -> str:
        return self._v3_api(
            f"/accounts/{_q(account_id)}/orders/{_q(order_id)}/decisions"
        )

    def _user_decisions_url(self, account_id: str, user_id: str) -> str:
        return self._v3_api(
            f"/accounts/{_q(account_id)}/users/{_q(user_id)}/decisions"
        )

    def _session_decisions_url(
        self, account_id: str, user_id: str, session_id: str
    ) -> str:
        return self._v3_api(
            f"/accounts/{_q(account_id)}/users/{_q(user_id)}/sessions/{_q(session_id)}/decisions"
        )

    def _content_decisions_url(
        self, account_id: str, user_id: str, content_id: str
    ) -> str:
        return self._v3_api(
            f"/accounts/{_q(account_id)}/users/{_q(user_id)}/content/{_q(content_id)}/decisions"
        )

    def _order_apply_decisions_url(
        self, account_id: str, user_id: str, order_id: str
    ) -> str:
        return self._v3_api(
            f"/accounts/{_q(account_id)}/users/{_q(user_id)}/orders/{_q(order_id)}/decisions"
        )

    def _psp_merchant_url(self, account_id: str) -> str:
        return self._v3_api(
            f"/accounts/{_q(account_id)}/psp_management/merchants"
        )

    def _psp_merchant_id_url(self, account_id: str, merchant_id: str) -> str:
        return self._v3_api(
            f"/accounts/{_q(account_id)}/psp_management/merchants/{_q(merchant_id)}"
        )

    def _verification_send_url(self) -> str:
        return self._v1_api("/verification/send")

    def _verification_resend_url(self) -> str:
        return self._v1_api("/verification/resend")

    def _verification_check_url(self) -> str:
        return self._v1_api("/verification/check")

    def _validate_send_request(self, properties: Mapping[str, t.Any]) -> None:
        """This method is used to validate arguments passed to the send method."""

        _assert_non_empty_dict(properties, "properties")

        user_id = properties.get("$user_id")
        _assert_non_empty_str(user_id, "user_id", error_cls=ValueError)

        send_to = properties.get("$send_to")
        _assert_non_empty_str(send_to, "send_to", error_cls=ValueError)

        verification_type = properties.get("$verification_type")
        _assert_non_empty_str(
            verification_type, "verification_type", error_cls=ValueError
        )

        event = properties.get("$event")
        if not isinstance(event, Mapping):
            raise TypeError("$event must be a mapping (dict)")
        elif not event:
            raise ValueError("$event mapping (dict) may not be empty")

        session_id = event.get("$session_id")
        _assert_non_empty_str(session_id, "session_id", error_cls=ValueError)

    def _validate_resend_request(
        self,
        properties: Mapping[str, t.Any],
    ) -> None:
        """This method is used to validate arguments passed to the send method."""

        _assert_non_empty_dict(properties, "properties")

        user_id = properties.get("$user_id")
        _assert_non_empty_str(user_id, "user_id", error_cls=ValueError)

    def _validate_check_request(self, properties: Mapping[str, t.Any]) -> None:
        """This method is used to validate arguments passed to the check method."""

        _assert_non_empty_dict(properties, "properties")

        user_id = properties.get("$user_id")
        _assert_non_empty_str(user_id, "user_id", error_cls=ValueError)

        if properties.get("$code") is None:
            raise ValueError("code is required")

    def _validate_apply_decision_request(
        self,
        properties: Mapping[str, t.Any],
        user_id: str,
    ) -> None:
        _assert_non_empty_str(user_id, "user_id")
        _assert_non_empty_dict(properties, "properties")

        source = properties.get("source")

        _assert_non_empty_str(source, "source", error_cls=ValueError)

        if source not in DECISION_SOURCES:
            raise ValueError(
                f"decision 'source' must be one of {list(DECISION_SOURCES)}"
            )

        if source == "MANUAL_REVIEW" and not properties.get("analyst"):
            raise ValueError(
                "must provide 'analyst' for decision 'source': 'MANUAL_REVIEW'"
            )

    def track(
        self,
        event: str,
        properties: Mapping[str, t.Any],
        path: str | None = None,
        return_score: bool = False,
        return_action: bool = False,
        return_workflow_status: bool = False,
        return_route_info: bool = False,
        force_workflow_run: bool = False,
        abuse_types: Sequence[str] | None = None,
        timeout: float | tuple[float, float] | None = None,
        version: str | None = None,
        include_score_percentiles: bool = False,
        include_warnings: bool = False,
    ) -> Response:
        """
        Track an event and associated properties to the Sift Science client.

        This call is blocking.

        Visit https://developers.sift.com/docs/python/events-api/
        for more information on what types of events you can send and fields
        you can add to the properties parameter.

        Args:
            event:
                The name of the event to send. This can either be a reserved
                event name such as "$transaction" or "$create_order" or
                a custom event name (that does not start with a $).

            properties:
                A mapping of additional event-specific attributes to track.

            path:
                An API endpoint to make a request to.
                Defaults to Events API Endpoint

            return_score (optional):
                Whether the API response should include a score for
                this user (the score will be calculated using this event).

            return_action (optional):
                Whether the API response should include actions in the
                response. For more information on how this works, please
                visit the tutorial at:
                https://developers.sift.com/tutorials/formulas

            return_workflow_status (optional):
                Whether the API response should include the status of any
                workflow run as a result of the tracked event.

            return_route_info (optional):
                Whether to get the route information from the Workflow
                Decision. This parameter must be used with the
                `return_workflow_status` query parameter.

            force_workflow_run (optional):
                Set to True to run the Workflow Asynchronously if your Workflow
                is set to only run on API Request. If a Workflow is not running
                on the event you send this with, there will be no error or
                score response, and no workflow will run.

            abuse_types (optional):
                A sequence of abuse types, specifying for which abuse types
                a score should be returned (if scores were requested). If not
                specified, a score will be returned for every abuse_type
                to which you are subscribed.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            version (optional):
                Use a different version of the Sift Science API for this call.

            include_score_percentiles (optional):
                Whether to add new parameter in the query parameter. if
                `include_score_percentiles` is True then add a new parameter
                called fields in the query parameter

            include_warnings (optional):
                Whether the API response should include `warnings` field.
                If `include_warnings` is True `warnings` field returns the
                amount of validation warnings along with their descriptions.
                They are not critical enough to reject the whole request,
                but important enough to be fixed.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(event, "event")
        _assert_non_empty_dict(properties, "properties")

        if version is None:
            version = self.version

        if path is None:
            path = self._events_url(version)

        if timeout is None:
            timeout = self.timeout

        _properties = {
            **properties,
            "$api_key": self.api_key,
            "$type": event,
        }

        params: dict[str, t.Any] = {}

        if return_score:
            params["return_score"] = "true"

        if return_action:
            params["return_action"] = "true"

        if abuse_types:
            params["abuse_types"] = ",".join(abuse_types)

        if return_workflow_status:
            params["return_workflow_status"] = "true"

        if return_route_info:
            params["return_route_info"] = "true"

        if force_workflow_run:
            params["force_workflow_run"] = "true"

        include_fields = self._get_fields_param(
            include_score_percentiles, include_warnings
        )

        if include_fields:
            params["fields"] = ",".join(include_fields)

        try:
            response = self.session.post(
                path,
                data=json.dumps(_properties, cls=DecimalEncoder),
                headers=self._post_headers(version),
                timeout=timeout,
                params=params,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), path)

        return Response(response)

    def score(
        self,
        user_id: str,
        timeout: float | tuple[float, float] | None = None,
        abuse_types: Sequence[str] | None = None,
        version: str | None = None,
        include_score_percentiles: bool = False,
    ) -> Response:
        """
        Retrieves a user's fraud score from the Sift Science API.

        This call is blocking.

        Visit https://developers.sift.com/docs/python/score-api/
        for more details on our Score response structure.

        Args:
            user_id:
                A user's id. This id should be the same as the `user_id`
                used in event calls.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            abuse_types (optional):
                A sequence of abuse types, specifying for which abuse types
                a score should be returned (if scores were requested). If not
                specified, a score will be returned for every abuse_type
                to which you are subscribed.

            version (optional):
                Use a different version of the Sift Science API for this call.

            include_score_percentiles (optional):
                Whether to add new parameter in the query parameter.
                if `include_score_percentiles` is True then add a new
                parameter called `fields` in the query parameter

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(user_id, "user_id")

        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        params: dict[str, t.Any] = {}

        if abuse_types:
            params["abuse_types"] = ",".join(abuse_types)

        if include_score_percentiles:
            params["fields"] = "SCORE_PERCENTILES"

        url = self._score_url(user_id, version)

        try:
            response = self.session.get(
                url,
                params=params,
                auth=self._auth,
                headers=self._default_headers(version),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_user_score(
        self,
        user_id: str,
        timeout: float | tuple[float, float] | None = None,
        abuse_types: Sequence[str] | None = None,
        include_score_percentiles: bool = False,
    ) -> Response:
        """
        Fetches the latest score(s) computed for the specified user and
        abuse types from the Sift Science API. As opposed to client.score()
        and client.rescore_user(), this *does not* compute a new score for
        the user; it simply fetches the latest score(s) which have computed.
        These scores may be arbitrarily old.

        This call is blocking.

        Visit https://developers.sift.com/docs/python/score-api/get-score/
        for more details.

        Args:
            user_id:
                A user's id. This id should be the same as the user_id used in
                event calls.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            abuse_types (optional):
                A sequence of abuse types, specifying for which abuse types
                a score should be returned (if scores were requested). If not
                specified, a score will be returned for every abuse_type
                to which you are subscribed.

            include_score_percentiles (optional):
                Whether to add new parameter in the query parameter.
                if include_score_percentiles is True then add a new parameter
                called fields in the query parameter

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(user_id, "user_id")

        if timeout is None:
            timeout = self.timeout

        url = self._user_score_url(user_id, self.version)
        params: dict[str, t.Any] = {}

        if abuse_types:
            params["abuse_types"] = ",".join(abuse_types)

        if include_score_percentiles:
            params["fields"] = "SCORE_PERCENTILES"

        try:
            response = self.session.get(
                url,
                params=params,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def rescore_user(
        self,
        user_id: str,
        timeout: float | tuple[float, float] | None = None,
        abuse_types: Sequence[str] | None = None,
    ) -> Response:
        """
        Rescores the specified user for the specified abuse types and returns
        the resulting score(s).

        This call is blocking.

        Visit https://developers.sift.com/docs/python/score-api/rescore/
        for more details.

        Args:
            user_id:
                A user's id. This id should be the same as the user_id used in
                event calls.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            abuse_types (optional):
                A sequence of abuse types, specifying for which abuse types
                a score should be returned (if scores were requested). If not
                specified, a score will be returned for every abuse_type
                to which you are subscribed.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(user_id, "user_id")

        if timeout is None:
            timeout = self.timeout

        url = self._user_score_url(user_id, self.version)
        params: dict[str, t.Any] = {}

        if abuse_types:
            params["abuse_types"] = ",".join(abuse_types)

        try:
            response = self.session.post(
                url,
                params=params,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def label(
        self,
        user_id: str,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
        version: str | None = None,
    ) -> Response:
        """
        Labels a user as either good or bad through the Sift Science API.

        This call is blocking.

        Visit https://developers.sift.com/docs/python/labels-api/label-user
        for more details on what fields to send in properties.

        Args:
            user_id:
                A user's id. This id should be the same as the user_id used in
                event calls.

            properties:
                A mapping of additional event-specific attributes to track.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            version (optional):
                Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(user_id, "user_id")

        if version is None:
            version = self.version

        return self.track(
            "$label",
            properties,
            path=self._labels_url(user_id, version),
            timeout=timeout,
            version=version,
        )

    def unlabel(
        self,
        user_id: str,
        timeout: float | tuple[float, float] | None = None,
        abuse_type: str | None = None,
        version: str | None = None,
    ) -> Response:
        """
        Unlabels a user through the Sift Science API.

        This call is blocking.

        Visit https://developers.sift.com/docs/python/labels-api/unlabel-user
        for more details.

        Args:
            user_id:
                A user's id. This id should be the same as the user_id used in
                event calls.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            abuse_type (optional):
                The abuse type for which the user should be unlabeled.
                If omitted, the user is unlabeled for all abuse types.

            version (optional):
                Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(user_id, "user_id")

        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        url = self._labels_url(user_id, version)
        params: dict[str, t.Any] = {}

        if abuse_type:
            params["abuse_type"] = abuse_type

        try:
            response = self.session.delete(
                url,
                params=params,
                auth=self._auth,
                headers=self._default_headers(version),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_workflow_status(
        self,
        run_id: str,
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Gets the status of a workflow run.

        Args:
            run_id:
                The workflow run unique identifier.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(run_id, "run_id")

        url = self._workflow_status_url(self.account_id, run_id)

        if timeout is None:
            timeout = self.timeout

        try:
            response = self.session.get(
                url,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_decisions(
        self,
        entity_type: t.Literal["user", "order", "session", "content"],
        limit: int | None = None,
        start_from: int | None = None,
        abuse_types: Sequence[str] | None = None,
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Get decisions available to the customer

        Args:
            entity_type:
                Return decisions applicable to entity type
                One of: "user", "order", "session", "content"

            limit (optional):
                Number of query results (decisions) to return [default: 100]

            start_from (optional):
                Result set offset for use in pagination [default: 0]

            abuse_types (optional):
                A sequence of abuse types, specifying by which abuse types
                decisions should be filtered.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(entity_type, "entity_type")

        if entity_type.lower() not in ("user", "order", "session", "content"):
            raise ValueError(
                "entity_type must be one of {user, order, session, content}"
            )

        if isinstance(abuse_types, str):
            raise ValueError(
                "Passing `abuse_types` as string is deprecated. "
                "Expected a sequence of string literals."
            )

        params: dict[str, t.Any] = {
            "entity_type": entity_type,
        }

        if limit:
            params["limit"] = limit

        if start_from:
            params["from"] = start_from

        if abuse_types:
            params["abuse_types"] = ",".join(abuse_types)

        if timeout is None:
            timeout = self.timeout

        url = self._decisions_url(self.account_id)

        try:
            response = self.session.get(
                url,
                params=params,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def apply_user_decision(
        self,
        user_id: str,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Apply decision to a user

        Args:
            user_id: id of a user

            properties:
                decision_id: decision to apply to a user
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                time: in millis when decision was applied

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(self.account_id, "account_id")

        self._validate_apply_decision_request(properties, user_id)

        if timeout is None:
            timeout = self.timeout

        url = self._user_decisions_url(self.account_id, user_id)

        try:
            response = self.session.post(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def apply_order_decision(
        self,
        user_id: str,
        order_id: str,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Apply decision to order

        Args:
            user_id:
                ID of a user.

            order_id:
                The ID for the order.

            properties:
                decision_id: decision to apply to order
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                description: free form text (optional)
                time: in millis when decision was applied (optional)

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(user_id, "user_id")
        _assert_non_empty_str(order_id, "order_id")

        self._validate_apply_decision_request(properties, user_id)

        if timeout is None:
            timeout = self.timeout

        url = self._order_apply_decisions_url(
            self.account_id, user_id, order_id
        )

        try:
            response = self.session.post(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_user_decisions(
        self,
        user_id: str,
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Gets the decisions for a user.

        Args:
            user_id:
                The ID of a user.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(user_id, "user_id")

        if timeout is None:
            timeout = self.timeout

        url = self._user_decisions_url(self.account_id, user_id)

        try:
            response = self.session.get(
                url,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_order_decisions(
        self,
        order_id: str,
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Gets the decisions for an order.

        Args:
            order_id:
                The ID for the order.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(order_id, "order_id")

        if timeout is None:
            timeout = self.timeout

        url = self._order_decisions_url(self.account_id, order_id)

        try:
            response = self.session.get(
                url,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_content_decisions(
        self,
        user_id: str,
        content_id: str,
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Gets the decisions for a piece of content.

        Args:
            user_id:
                The ID of the owner of the content.

            content_id:
                The ID for the content.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(content_id, "content_id")
        _assert_non_empty_str(user_id, "user_id")

        if timeout is None:
            timeout = self.timeout

        url = self._content_decisions_url(self.account_id, user_id, content_id)

        try:
            response = self.session.get(
                url,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_session_decisions(
        self,
        user_id: str,
        session_id: str,
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Gets the decisions for a user's session.

        Args:
            user_id:
                The ID for the user.

            session_id:
                The ID for the session.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(user_id, "user_id")
        _assert_non_empty_str(session_id, "session_id")

        if timeout is None:
            timeout = self.timeout

        url = self._session_decisions_url(self.account_id, user_id, session_id)

        try:
            response = self.session.get(
                url,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def apply_session_decision(
        self,
        user_id: str,
        session_id: str,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Apply decision to a session.

        Args:
            user_id:
                The ID for the user.

            session_id:
                The ID for the session.

            properties:
                decision_id: decision to apply to session
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                description: free form text (optional)
                time: in millis when decision was applied (optional)

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(user_id, "user_id")
        _assert_non_empty_str(session_id, "session_id")

        self._validate_apply_decision_request(properties, user_id)

        if timeout is None:
            timeout = self.timeout

        url = self._session_decisions_url(self.account_id, user_id, session_id)

        try:
            response = self.session.post(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def apply_content_decision(
        self,
        user_id: str,
        content_id: str,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Apply decision to a piece of content.

        Args:
            user_id:
                The ID for the user.

            content_id:
                The ID for the content.

            properties:
                decision_id: decision to apply to session
                source: {one of MANUAL_REVIEW | AUTOMATED_RULE | CHARGEBACK}
                analyst: id or email, required if 'source: MANUAL_REVIEW'
                description: free form text (optional)
                time: in millis when decision was applied (optional)

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        _assert_non_empty_str(self.account_id, "account_id")
        _assert_non_empty_str(user_id, "user_id")
        _assert_non_empty_str(content_id, "content_id")

        self._validate_apply_decision_request(properties, user_id)

        if timeout is None:
            timeout = self.timeout

        url = self._content_decisions_url(self.account_id, user_id, content_id)

        try:
            response = self.session.post(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def create_psp_merchant_profile(
        self,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Create a new PSP Merchant profile

        Args:
            properties:
                A mapping of merchant profile data.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")

        if timeout is None:
            timeout = self.timeout

        url = self._psp_merchant_url(self.account_id)

        try:
            response = self.session.post(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def update_psp_merchant_profile(
        self,
        merchant_id: str,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Update already existing PSP Merchant profile

        Args:
            merchant_id:
                The internal identifier for the merchant or seller providing
                the good or service.

            properties:
                A mapping of merchant profile data.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")

        if timeout is None:
            timeout = self.timeout

        url = self._psp_merchant_id_url(self.account_id, merchant_id)

        try:
            response = self.session.put(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_psp_merchant_profiles(
        self,
        batch_token: str | None = None,
        batch_size: int | None = None,
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Gets all PSP merchant profiles (paginated).

        Args:
            batch_token (optional):
                Batch or page position of the paginated sequence.

            batch_size: (optional):
                Batch or page size of the paginated sequence.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")

        if timeout is None:
            timeout = self.timeout

        url = self._psp_merchant_url(self.account_id)

        params: dict[str, t.Any] = {}

        if batch_size:
            params["batch_size"] = batch_size

        if batch_token:
            params["batch_token"] = batch_token

        try:
            response = self.session.get(
                url,
                auth=self._auth,
                headers=self._default_headers(),
                params=params,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def get_a_psp_merchant_profile(
        self,
        merchant_id: str,
        timeout: float | tuple[float, float] | None = None,
    ) -> Response:
        """Gets a PSP merchant profile by merchant id.

        Args:
            merchant_id:
                The internal identifier for the merchant or seller providing
                the good or service.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        _assert_non_empty_str(self.account_id, "account_id")

        if timeout is None:
            timeout = self.timeout

        url = self._psp_merchant_id_url(self.account_id, merchant_id)

        try:
            response = self.session.get(
                url,
                auth=self._auth,
                headers=self._default_headers(),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def verification_send(
        self,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
        version: str | None = None,
    ) -> Response:
        """
        The send call triggers the generation of an OTP code that is stored
        by Sift and email/sms the code to the user.

        This call is blocking.

        Visit https://developers.sift.com/docs/python/verification-api/send
        for more details on our send response structure.

        Args:
            properties:

                $user_id:
                    User ID of user being verified, e.g. johndoe123.
                $send_to:
                    The phone / email to send the OTP to.
                $verification_type:
                    The channel used for verification. Should be either $email
                    or $sms.
                $brand_name (optional):
                    Name of the brand of product or service the user interacts
                    with.
                $language (optional):
                    Language of the content of the web site.
                $site_country (optional):
                    Country of the content of the site.
                $event:
                    $session_id:
                        The session being verified. See $verification in the
                        Sift Events API documentation.
                    $verified_event:
                        The type of the reserved event being verified.
                    $reason (optional):
                        The trigger for the verification. See $verification
                        in the Sift Events API documentation.
                    $ip (optional):
                        The user's IP address.
                    $browser:
                        $user_agent:
                            The user agent of the browser that is verifying.
                            Represented by the $browser object.
                            Use this field if the client is a browser.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            version (optional):
                Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        self._validate_send_request(properties)

        url = self._verification_send_url()

        try:
            response = self.session.post(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(version),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def verification_resend(
        self,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
        version: str | None = None,
    ) -> Response:
        """
        A user can ask for a new OTP (one-time password) if they haven't
        received the previous one, or in case the previous OTP expired.

        This call is blocking.

        Visit https://developers.sift.com/docs/python/verification-api/resend
        for more information on our send response structure.

        Args:

            properties:
                $user_id:
                    User ID of user being verified, e.g. johndoe123.
                $verified_event (optional):
                    This will be the event type that triggered the verification.
                $verified_entity_id (optional):
                    The ID of the entity impacted by the event being verified.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            version (optional):
                Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """

        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        self._validate_resend_request(properties)

        url = self._verification_resend_url()

        try:
            response = self.session.post(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(version),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)

    def verification_check(
        self,
        properties: Mapping[str, t.Any],
        timeout: float | tuple[float, float] | None = None,
        version: str | None = None,
    ) -> Response:
        """
        The verification_check call is used for checking the OTP provided by
        the end user to Sift. Sift then compares the OTP, checks rate limits
        and responds with a decision whether the user should be able to
        proceed or not.

        This call is blocking.

        Visit https://developers.sift.com/docs/python/verification-api/check
        for more information on our check response structure.

        Args:

            properties:

                $user_id:
                    User ID of user being verified, e.g. johndoe123.
                $code:
                    The code the user sent to the customer for validation.
                $verified_event (optional):
                    This will be the event type that triggered the verification.
                $verified_entity_id (optional):
                    The ID of the entity impacted by the event being verified.

            timeout (optional):
                How many seconds to wait for the server to send data before
                giving up, as a float, or a (connect timeout, read timeout) tuple.

            version (optional):
                Use a different version of the Sift Science API for this call.

        Returns:
            A sift.client.Response object if the call to the Sift API is successful

        Raises:
            ApiException: If the call to the Sift API is not successful
        """
        if timeout is None:
            timeout = self.timeout

        if version is None:
            version = self.version

        self._validate_check_request(properties)

        url = self._verification_check_url()

        try:
            response = self.session.post(
                url,
                data=json.dumps(properties),
                auth=self._auth,
                headers=self._post_headers(version),
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), url)

        return Response(response)
