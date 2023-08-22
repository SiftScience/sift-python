import sift

from os import environ as env
 # Get the value of API_KEY from environment variable
api_key = env['API_KEY']
client = sift.Client(api_key = api_key)

def create_order_with_return_score():
  # Sample $create_order event
  order_properties = {
    # Required Fields
    "$user_id"                   : "billy_jones_301",
    # Supported Fields
    "$session_id"                : "gigtleqddo84l8cm15qe4il",
    "$order_id"                  : "ORDER-28168441",
    "$user_email"                : "billjones1@example.com",
    "$verification_phone_number" : "+123456789012",
    "$amount"                    : 115940000, # $115.94
    "$currency_code"             : "USD",
    "$billing_address"           : {
        "$name"         : "Bill Jones",
        "$phone"        : "1-415-555-6041",
        "$address_1"    : "2100 Main Street",
        "$address_2"    : "Apt 3B",
        "$city"         : "New London",
        "$region"       : "New Hampshire",
        "$country"      : "US",
        "$zipcode"      : "03257"
    },
    "$payment_methods"  : [
        {
            "$payment_type"    : "$credit_card",
            "$payment_gateway" : "$braintree",
            "$card_bin"        : "542486",
            "$card_last4"      : "4444"
        }
    ],
    "$ordered_from" : {
      "$store_id"      : "123",
      "$store_address" : {
        "$name"       : "Bill Jones",
        "$phone"      : "1-415-555-6040",
        "$address_1"  : "2100 Main Street",
        "$address_2"  : "Apt 3B",
        "$city"       : "New London",
        "$region"     : "New Hampshire",
        "$country"    : "US",
        "$zipcode"    : "03257"
      }
    },
    "$brand_name"   : "sift",
    "$site_domain"  : "sift.com",
    "$site_country" : "US",
    "$shipping_address"  : {
        "$name"          : "Bill Jones",
        "$phone"         : "1-415-555-6041",
        "$address_1"     : "2100 Main Street",
        "$address_2"     : "Apt 3B",
        "$city"          : "New London",
        "$region"        : "New Hampshire",
        "$country"       : "US",
        "$zipcode"       : "03257"
    },
    "$expedited_shipping"       : True,
    "$shipping_method"          : "$physical",
    "$shipping_carrier"         : "UPS",
    "$shipping_tracking_numbers": ["1Z204E380338943508", "1Z204E380338943509"],
    "$items"                    : [
      {
        "$item_id"        : "12344321",
        "$product_title"  : "Microwavable Kettle Corn: Original Flavor",
        "$price"          : 4990000, # $4.99
        "$upc"            : "097564307560",
        "$sku"            : "03586005",
        "$brand"          : "Peters Kettle Corn",
        "$manufacturer"   : "Peters Kettle Corn",
        "$category"       : "Food and Grocery",
        "$tags"           : ["Popcorn", "Snacks", "On Sale"],
        "$quantity"       : 4
      },
      {
        "$item_id"        : "B004834GQO",
        "$product_title"  : "The Slanket Blanket-Texas Tea",
        "$price"          : 39990000, # $39.99
        "$upc"            : "6786211451001",
        "$sku"            : "004834GQ",
        "$brand"          : "Slanket",
        "$manufacturer"   : "Slanket",
        "$category"       : "Blankets & Throws",
        "$tags"           : ["Awesome", "Wintertime specials"],
        "$color"          : "Texas Tea",
        "$quantity"       : 2
      }
    ],
    # For marketplaces, use $seller_user_id to identify the seller
    "$seller_user_id"     : "slinkys_emporium",

    "$promotions"         : [
      {
        "$promotion_id" : "FirstTimeBuyer",
        "$status"       : "$success",
        "$description"  : "$5 off",
        "$discount"     : {
          "$amount"                   : 5000000,  # $5.00
          "$currency_code"            : "USD",
          "$minimum_purchase_amount"  : 25000000  # $25.00
        }
      }
    ],

    # Sample Custom Fields
    "digital_wallet"      : "apple_pay", # "google_wallet", etc.
    "coupon_code"         : "dollarMadness",
    "shipping_choice"     : "FedEx Ground Courier",
    "is_first_time_buyer" : False,

    # Send this information from a BROWSER client.
    "$browser"      : {
      "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
      "$accept_language"  : "en-US",
      "$content_language" : "en-GB"
    }
  }

  response = client.track("$create_order", order_properties, return_score= True, abuse_types=['payment_abuse', 'promotion_abuse'])
  print(response)
  assert(response.is_ok())
  assert response.api_status == 0, "api_status should be 0"
  assert response.api_error_message == "OK", "api_error_message should be OK"

def get_score():
    response = client.score("haneeshv@exalture.com")
    print(response)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def get_user_score():
    response = client.get_user_score("haneeshv@exalture.com")
    print(response)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def rescore_user():
    response = client.rescore_user("haneeshv@exalture.com", abuse_types=['payment_abuse', 'account_abuse'])
    print(response)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"