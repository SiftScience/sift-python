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

-   Added Unlabel functionaly
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

