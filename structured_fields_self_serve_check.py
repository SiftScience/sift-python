"""
NEB-4783 QA self-serve check, section D (client libraries) - Python.

IMPORTANT: none of the 6 client library PRs (Java, .NET, Python, PHP, Ruby) are merged
or released yet. This only works against a local checkout of this branch - installing
the published sift-python package from PyPI will NOT have these fields.

The Python client does zero field validation - it just passes through whatever keys
you put in the properties dict. So there's no "compile-time safety" story here like
Java/.NET; this script only proves the round trip against prod actually works.

How to run:
    SIFT_QA_API_KEY=... python3 structured_fields_self_serve_check.py

Each call reuses the exact payload shapes already verified in section A's Postman
collection. All 7 should print "status: 0" - if any doesn't, that's a real finding.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sift.client import Client  # noqa: E402

USER_ID = "qa_structured_fields_2026"
ORDER_ID = "qa_order_001"


def check(label, event_type, properties):
    response = client.track(event_type, properties)
    print(f"[{label}] http_status_code={response.http_status_code} "
          f"api_status={response.api_status} "
          f"api_error_message={response.api_error_message}")
    if response.api_status != 0 or response.http_status_code != 200:
        print(f"[{label}] UNEXPECTED - expected status 0 / http 200")


def main():
    global client
    api_key = os.environ.get("SIFT_QA_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set SIFT_QA_API_KEY first - see the comment at the top of this file.")
    client = Client(api_key=api_key, account_id=USER_ID)

    check("create_account", "$create_account", {
        "$user_id": USER_ID,
        "$nationality": "US",
        "$year_of_birth": 1985,
        "$kyc": {
            "$names_match": True,
            "$kyc_level": "$basic",
            "$bin_nationality_match": True,
            "$provider": "lexisnexis",
        },
        "$geo": {"$uuid": "gc-abc-123", "$provider": "geocomply"},
        "$bot_identification": {"$result": "$human", "$provider": "datadome"},
    })

    check("update_account", "$update_account", {
        "$user_id": USER_ID,
        "$nationality": "US",
        "$year_of_birth": 1985,
        "$kyc": {
            "$names_match": True,
            "$kyc_level": "$full",
            "$bin_nationality_match": True,
            "$provider": "lexisnexis",
        },
        "$geo": {"$uuid": "gc-abc-123", "$provider": "geocomply"},
        "$bot_identification": {"$result": "$human", "$provider": "datadome"},
    })

    check("login", "$login", {
        "$user_id": USER_ID,
        "$login_status": "$success",
        "$geo": {"$uuid": "gc-abc-123", "$provider": "geocomply"},
        "$bot_identification": {"$result": "$human", "$provider": "datadome"},
    })

    check("transaction", "$transaction", {
        "$user_id": USER_ID,
        "$amount": 15230000,
        "$currency_code": "USD",
        "$kyc": {
            "$names_match": True,
            "$kyc_level": "$full",
            "$bin_nationality_match": False,
            "$provider": "prove",
        },
        "$geo": {"$uuid": "gc-abc-123", "$provider": "geocomply"},
        "$bot_identification": {"$result": "$human", "$provider": "human_security"},
    })

    check("create_order", "$create_order", {
        "$user_id": USER_ID,
        "$order_id": ORDER_ID,
        "$kyc": {
            "$names_match": True,
            "$kyc_level": "$basic",
            "$bin_nationality_match": True,
            "$provider": "lexisnexis",
        },
        "$geo": {"$uuid": "gc-abc-123", "$provider": "geocomply"},
        "$bot_identification": {"$result": "$human", "$provider": "datadome"},
    })

    check("update_order", "$update_order", {
        "$user_id": USER_ID,
        "$order_id": ORDER_ID,
        "$kyc": {
            "$names_match": True,
            "$kyc_level": "$basic",
            "$bin_nationality_match": True,
            "$provider": "lexisnexis",
        },
        "$geo": {"$uuid": "gc-abc-123", "$provider": "geocomply"},
        "$bot_identification": {"$result": "$human", "$provider": "datadome"},
    })

    # No $geo/$bot_identification here on purpose - $verification only supports $kyc
    # per the attachment matrix.
    check("verification", "$verification", {
        "$user_id": USER_ID,
        "$verification_type": "$kyc",
        "$status": "$success",
        "$kyc": {
            "$names_match": True,
            "$kyc_level": "$basic",
            "$bin_nationality_match": False,
            "$provider": "lexisnexis",
        },
    })


if __name__ == "__main__":
    main()
