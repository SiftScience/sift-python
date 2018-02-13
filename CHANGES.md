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

