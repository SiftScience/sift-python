============================
Sift Science Python Bindings
============================

Bindings for Sift Science's `REST API <https://siftscience.com/docs/rest-api>`_.

Installation
============

Get the package from pip (may be outdated):

::

    pip install sift

or install directly from GitHub:

::

    pip install git+https://github.com/SiftScience/sift-python


Usage
=====

Here's an example:

::

    import sift.Client

    api_key = 'XXXXXXXXXXXXXX'  # TODO
    sift_client = sift.Client(api_key)

    # Track a transaction event -- note this is blocking
    sift_client.track('$transaction', {
        '$user_id': '23056',
        '$user_email': 'buyer@gmail.com',
        '$seller_user_id': '2371',
        '$seller_user_email': 'seller@gmail.com',
        '$transaction_id': '573050',
        '$currency_code': 'USD',
        '$amount': 15230000,
        '$time': 1327604222,
        'trip_time': 930,
        'distance_traveled': 5.26,
    })
