# Sift Python Bindings

Bindings for Sift's APIs -- including the
[Events](https://sift.com/resources/references/events-api.html),
[Labels](https://sift.com/resources/references/labels-api.html),
and
[Score](https://sift.com/resources/references/score-api.html)
APIs.


## Installation

Set up a virtual environment with virtualenv (otherwise you will need
to make the pip calls as sudo):

    virtualenv venv
    source venv/bin/activate

Get the latest released package from pip:

Python 2:

    pip install Sift

Python 3:

    pip3 install Sift

or install newest source directly from GitHub:

Python 2:

    pip install git+https://github.com/SiftScience/sift-python

Python 3:

    pip3 install git+https://github.com/SiftScience/sift-python


## Documentation

Please see [here](https://sift.com/developers/docs/python/events-api/overview) for the
most up-to-date documentation.

## Changelog

Please see
[the CHANGELOG](https://github.com/SiftScience/sift-python/blob/master/CHANGES.md)
for a history of all changes.

Note, that in v2.0.0, the API semantics were changed to raise an
exception in the case of error to be more pythonic. Client code will
need to be updated to catch `sift.client.ApiException` exceptions.


## Usage

Here's an example:

```python

import json
import sift.client

client = sift.Client(api_key='<your API key here>', account_id='<your account ID here>')

# User ID's may only contain a-z, A-Z, 0-9, =, ., -, _, +, @, :, &, ^, %, !, $
user_id = "23056"

# Track a transaction event -- note this is a blocking call
properties = {
    "$user_id": user_id,
    "$user_email": "buyer@gmail.com",
    "$seller_user_id": "2371",
    "seller_user_email": "seller@gmail.com",
    "$transaction_id": "573050",
    "$payment_method": {
        "$payment_type": "$credit_card",
        "$payment_gateway": "$braintree",
        "$card_bin": "542486",
        "$card_last4": "4444"
    },
    "$currency_code": "USD",
    "$amount": 15230000,
}

try:
    response = client.track("$transaction", properties)
    if response.is_ok():
        print "Successfully tracked event"
except sift.client.ApiException:
    # request failed
    pass

# Request a score for the user with user_id 23056
try:
    response = client.score(user_id)
    s = json.dumps(response.body)
    print s

except sift.client.ApiException:
    # request failed
    pass

try:
    # Label the user with user_id 23056 as Bad with all optional fields
    response = client.label(user_id, {
        "$is_bad": True,
        "$abuse_type": "payment_abuse",
        "$description": "Chargeback issued",
        "$source": "Manual Review",
        "$analyst": "analyst.name@your_domain.com"
    })
except sift.client.ApiException:
    # request failed
    pass

# Remove a label from a user with user_id 23056
try:
    response = client.unlabel(user_id, abuse_type='content_abuse')
except sift.client.ApiException:
    # request failed
    pass

# Get the status of a workflow run
try:
    response = client.get_workflow_status('my_run_id')
except sift.client.ApiException:
    # request failed
    pass

# Get the latest decisions for a user
try:
    response = client.get_user_decisions('example_user')
except sift.client.ApiException:
    # request failed
    pass

# Get the latest decisions for an order
try:
    response = client.get_order_decisions('example_order')
except sift.client.ApiException:
    # request failed
    pass

# Get the latest decisions for a session
try:
    response = client.get_session_decisions('example_user', 'example_session')
except sift.client.ApiException:
    # request failed
    pass

# Get the latest decisions for a piece of content
try:
    response = client.get_content_decisions('example_user', 'example_content')
except sift.client.ApiException:
    # request failed
    pass
```


## Testing

Before submitting a change, make sure the following commands run without
errors from the root dir of the repository:

    python -m unittest discover
    python3 -m unittest discover
