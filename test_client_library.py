from decimal import Decimal
import sift
import sys
from os import environ as env

if sys.version_info[0] < 3:
    import six.moves.urllib as urllib 
else:
    import urllib.parse

def response_with_data_header():
    return {
        'content-type': 'application/json; charset=UTF-8'
    }

# Get the value of API_KEY from environment variable
api_key = env['API_KEY']

def test_add_item_to_cart():
    add_item_to_cart_properties = {       
         # Required Fields
        "$user_id"           : "haneeshv@exalture.com",

        # Supported Fields
        "$session_id" : "gigtleqddo84l8cm15qe4il",
        "$item"       : {
            "$item_id"        : "B004834GQO",
            "$product_title"  : "The Slanket Blanket-Texas Tea",
            "$price"          : 39990000, # $39.99
            "$currency_code"  : "USD",
            "$upc"            : "6786211451001",
            "$sku"            : "004834GQ",
            "$brand"          : "Slanket",
            "$manufacturer"   : "Slanket",
            "$category"       : "Blankets & Throws",
            "$tags"           : ["Awesome", "Wintertime specials"],
            "$color"          : "Texas Tea",
            "$quantity"       : 16
        },
        "$brand_name"   : "sift",
        "$site_domain"  : "sift.com",
        "$site_country" : "US",
        # Send this information from a BROWSER client.
        "$browser"      : {
            "$user_agent"       : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "$accept_language"  : "en-US",
            "$content_language" : "en-GB"
        }
    }
    client = sift.Client(api_key=api_key, account_id='ACCT')
    response = client.track("$add_item_to_cart", add_item_to_cart_properties)
    print(response)

test_add_item_to_cart()