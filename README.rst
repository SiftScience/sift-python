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

    import sift.client

    api_key = 'XXXXXXXXXXXXXX'  # TODO
    sift_client = sift.Client(api_key)

    # Track a transaction event -- note this is blocking
    response = sift_client.track('$transaction', {
        '$user_id': '23056',
        '$user_email': 'buyer@gmail.com',
        '$seller_user_id': '2371',
        'seller_user_email': 'seller@gmail.com',
        '$transaction_id': '573050',
        '$currency_code': 'USD',
        '$amount': 15230000,
        '$time': 1327604222,
        'trip_time': 930,
        'distance_traveled': 5.26,
    })
    
    response.is_ok()
    True
    
    print response
    {"body": {"status": 0, "error_message": "OK", "request": "{\"$type\": \"$transaction\", \"$transaction_id\": \"573050\", \"$amount\": 15230000, \"seller_user_email\": \"seller@gmail.com\", \"distance_traveled\": 5.26, \"$api_key\": \"1a3e7a7bb8428f10\", \"$user_email\": \"buyer@gmail.com\", \"$seller_user_id\": \"2371\", \"trip_time\": 930, \"$user_id\": \"23056\", \"$currency_code\": \"USD\", \"$time\": 1327604222}", "time": 1407545773}, "http_status_code": 200}
