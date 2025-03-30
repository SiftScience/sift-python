6.0.0 (Not released yet)
================

- Added support for Python 3.13
- Dropped support for Python < 3.8
- Added typing annotations overall the library
- Updated doc strings with actual information
- Fixed an issue when the client could send requests with invalid version in the "User-Agent" header
- Changed the type of the `abuse_types` parameter in the `client.get_decisions()` method

INCOMPATIBLE CHANGES INTRODUCED IN 6.0.0:

- Dropped support for Python < 3.8
- Passing `abuse_types` as a comma-separated string to the `client.get_decisions()` is deprecated.

  Previously, `client.get_decisions()` method allowed to pass `abuse_types` parameter as a
  comma-separated string e.g. `abuse_types="legacy,payment_abuse"`. This is deprecated now.
  Starting from 6.0.0 callers must pass `abuse_types` parameter to the `client.get_decisions()`
  method as a sequence of string literals e.g. `abuse_types=("legacy", "payment_abuse")`. The same
  way as it passed to the other client's methods which receive `abuse_types` parameter.

5.6.1 2024-10-08
- Updated implementation to use Basic Authentication instead of passing `API_KEY` as a request parameter for the following calls:
  - `client.score()`
  - `client.get_user_score()`
  - `client.rescore_user()`
  - `client.unlabel()`

5.6.0 2024-05-31
- Added support for a `warnings` value in the `fields` query parameter

5.5.1 2024-02-22
- Support for Python 3.12

5.5.0 2023-10-03
- Score percentiles for Score API

5.4.0 2023-07-26
- Support for Verification API

5.3.0 2023-02-03
- Added support for score_percentiles

5.2.0 2022-11-07
- Update  PSP Merchant Management API

5.1.0 2022-06-22
- Added return_route_info query parameter 
- Fixed decimal amount json serialization bug 

5.0.2 2022-01-24
- Fix usage of urllib for Python 2.7

5.0.1 2019-03-07
- Update metadata in setup.py

5.0.0 2019-01-08
================
- Add connection pooling

INCOMPATIBLE CHANGES INTRODUCED IN 5.0.0:

- Removed support for Python 2.6

- Fix url encoding for all endpoints

  Previously, encoding user ids in URLs was inconsistent between endpoints, encoded for some
  endpoints, unencoded for others. Additionally, when encoded in the URL path, forward slashes
  weren't encoded. Callers with workarounds for this bug must remove these workarounds when
  upgrading to 5.0.0.

- Improved error handling

  Previously, illegal arguments passed to methods like `Client.track()` and failed calls resulting
  from server-side errors both raised `ApiExceptions`. Illegal arguments validated in the client
  now raise either `TypeErrors` or `ValueErrors`. Server-side errors still raise `ApiExceptions`,
  and `ApiException` has been augmented with metadata for handling the error.

4.3.0.0 2018-07-31
==================
-   Add support for rescore_user and get_user_score APIs

4.2.0.0 2018-07-05
==================
-   Add new query parameter force_workflow_run

4.1.0.0 2018-06-01
==================

-   Add get session level decisions in Get Decisions APIs.

4.0.1 2018-04-06
==================

- Updated documentation in CHANGES.md and README.md

4.0.0.0 2018-03-30
==================

- Adds support for Sift Science API Version 205, including new [`$create_content`](https://siftscience.com/developers/docs/curl/events-api/reserved-events/create-content) and [`$update_content`](https://siftscience.com/developers/docs/curl/events-api/reserved-events/update-content) formats
- V205 APIs are now called -- **this is an incompatible change**
   - Use `version = '204'` when constructing the Client to call the previous API version
- Adds support for content decisions to [Decisions API](https://siftscience.com/developers/docs/curl/decisions-api)


INCOMPATIBLE CHANGES INTRODUCED IN API V205:
- `$create_content` and `$update_content` have significantly changed, and the old format will be rejected
- `$send_message` and `$submit_review` events are no longer valid
- V205 improves server-side event data validation. In V204 and earlier, server-side validation accepted some events that did not conform to the published APIs in our [developer documentation](https://siftscience.com/developers/docs/curl/events-api). V205 does not modify existing event APIs other than those mentioned above, but may reject invalid event data that were previously accepted. **Please test your integration on V205 in sandbox before using in production.**

3.2.0.0 2018-02-12
==================

-   Add session level decisions in Apply Decisions APIs.
-   Add support for filtering get decisions by entity type session.

3.1.0.0 2017-01-17
==================

-   Adds support for Get, Apply Decisions APIs

3.0.0.0 2016-07-19
==================

-   Adds support for v204 of Sift Science's APIs
-   Adds Workflow Status API, User Decisions API, Order Decisions API
-   V204 APIs are now called by default -- this is an incompatible change
    (use version='203' to call the previous API version)

2.0.1.0 (2016-07-07)
====================

-   Fixes bug parsing chunked HTTP responses

2.0.0.0 (2016-06-21)
====================

-   Major version bump; client APIs have changed to raise exceptions
    in the case of API errors to be more Pythonic

1.1.2.1 (2015-05-18)
====================

-   Added Python 2.6 compatibility
-   Added Travis CI
-   Minor bug fixes

1.1.2.0 (2015-02-04)
====================

-   Added Unlabel functionality
-   Minor bug fixes.

1.1.1.0 (2014-09-3)
===================

-   Added timeout parameter to track, score, and label functions.

1.1.0.0 (2014-08-25)
====================

-   Added Module-scoped API key.
-   Minor documentation updates.

0.2.0 (2014-08-20)
==================

-   Added Label and Score functions.
-   Added Python 3 compatibility.

0.1.1 (2014-02-21)
==================

-   Bump default API version to v203.

0.1.0 (2013-01-08)
==================

-   Just the Python REST client itself.
