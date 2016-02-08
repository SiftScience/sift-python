============================
Sift Science Python Bindings |TravisCI|_
============================

.. |TravisCI| image:: https://travis-ci.org/SiftScience/sift-python.png?branch=master
.. _TravisCI: https://travis-ci.org/SiftScience/sift-python

Bindings for Sift Science's `Events <https://siftscience.com/resources/references/events-api.html>`_, `Labels <https://siftscience.com/resources/references/labels-api.html>`_, and `Score <https://siftscience.com/resources/references/score-api.html>`_ APIs.

Installation
============

Set up a virtual environment with virtualenv (otherwise you will need to make the pip calls as sudo):
::

    virtualenv venv
    source venv/bin/activate

Get the latest released package from pip:

Python 2:
::

    pip install sift

Python 3:
::

    pip3 install sift
    
or install newest source directly from GitHub:

Python 2:
::

    pip install git+https://github.com/SiftScience/sift-python

Python 3:
::

    pip3 install git+https://github.com/SiftScience/sift-python
    
Usage
=====

Here's an example:

::

    import sift.client

    sift.api_key = '<your api key here>'
    client = sift.Client()

    user_id= "23056"   # User ID's may only contain a-z, A-Z, 0-9, =, ., -, _, +, @, :, &, ^, %, !, $
    
    # Track a transaction event -- note this is blocking
    event = "$transaction"

    properties = {
      "$user_id" : user_id, 
      "$user_email" : "buyer@gmail.com", 
      "$seller_user_id" : "2371", 
      "seller_user_email" : "seller@gmail.com", 
      "$transaction_id" : "573050", 
      "$payment_method" : {
        "$payment_type"    : "$credit_card",
        "$payment_gateway" : "$braintree",
        "$card_bin"        : "542486",
        "$card_last4"      : "4444"             
      }, 
      "$currency_code" : "USD",
      "$amount" : 15230000,
    }

    response = client.track(event, properties)

    
    response.is_ok()  # returns True of False
    
    print response # prints entire response body and http status code
    
    
    # Request a score for the user with user_id 23056
    response = client.score(user_id)
    
    # Label the user with user_id 23056 as Bad with all optional fields
    response = client.label(user_id,{ "$is_bad" : True, "$reasons" : ["$chargeback", ],
                            "$description" : "Chargeback issued",
                            "$source" : "Manual Review",
                            "$analyst" : "analyst.name@your_domain.com"})

    # Remove a label from a user with user_id 23056
    response = client.unlabel(user_id)

Testing
=======

Before submitting a change, make sure the following commands run without errors from the root dir of the repository:

::

    PYTHONPATH=. python tests/client_test.py
    PYTHONPATH=. python3 tests/client_test.py
