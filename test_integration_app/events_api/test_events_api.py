import sift
import globals

from os import environ as env

class EventsAPI():
  # Get the value of API_KEY from environment variable
  api_key = env['API_KEY']
  client = sift.Client(api_key = api_key)
  globals.initialize()
  user_id = globals.user_id
  user_email = globals.user_email
  
  def add_item_to_cart(self):
    add_item_to_cart_properties = {       
      # Required Fields
      "$user_id"           : self.user_id,
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
    return self.client.track("$add_item_to_cart", add_item_to_cart_properties)
    

  def add_promotion(self):
    add_promotion_properties = {
      # Required fields.
      "$user_id"    : self.user_id,
      # Supported fields.
      "$promotions" : [
        # Example of a promotion for monetary discounts off good or services
        {
          "$promotion_id"     : "NewRideDiscountMay2016",
          "$status"           : "$success",
          "$description"      : "$5 off your first 5 rides",
          "$referrer_user_id" : "elon-m93903",
          "$discount"         : {
            "$amount"         : 5000000,  # $5
            "$currency_code"  : "USD"
          }
        }
      ],
      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$add_promotion", add_promotion_properties)

  def chargeback(self):
    # Sample $chargeback event
    chargeback_properties = {
      # Required Fields
      "$order_id"          : "ORDER-123124124",
      "$transaction_id"    : "719637215",
      # Recommended Fields
      "$user_id"           : self.user_id,
      "$chargeback_state"  : "$lost",
      "$chargeback_reason" : "$duplicate"
    }
    return self.client.track("$chargeback", chargeback_properties)

  def content_status(self):
    # Sample $content_status event
    content_status_properties = {
      # Required Fields
      "$user_id"    : self.user_id,
      "$content_id" : "9671500641",
      "$status"     : "$paused",

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$content_status", content_status_properties)

  def create_account(self):
    # Sample $create_account event
    create_account_properties = {
      # Required Fields
      "$user_id"    : self.user_id,
      # Supported Fields
      "$session_id"                : "gigtleqddo84l8cm15qe4il",
      "$user_email"                : self.user_email,
      "$verification_phone_number" : "+123456789012",
      "$name"                      : "Bill Jones",
      "$phone"                     : "1-415-555-6040",
      "$referrer_user_id"          : "janejane101",
      "$payment_methods"           : [
        {
          "$payment_type"    : "$credit_card",
          "$card_bin"        : "542486",
          "$card_last4"      : "4444"
        }
      ],
      "$billing_address"  : {
        "$name"         : "Bill Jones",
        "$phone"        : "1-415-555-6040",
        "$address_1"    : "2100 Main Street",
        "$address_2"    : "Apt 3B",
        "$city"         : "New London",
        "$region"       : "New Hampshire",
        "$country"      : "US",
        "$zipcode"      : "03257"
      },
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
      "$promotions"       : [
        {
          "$promotion_id"     : "FriendReferral",
          "$status"           : "$success",
          "$referrer_user_id" : "janejane102",
          "$credit_point"     : {
            "$amount"              : 100,
            "$credit_point_type"   : "account karma"
          }
        }
      ],
      "$social_sign_on_type"   : "$twitter",
      "$account_types"         : ["merchant", "premium"],

      # Suggested Custom Fields
      "twitter_handle"          : "billyjones",
      "work_phone"              : "1-347-555-5921",
      "location"                : "New London, NH",
      "referral_code"           : "MIKEFRIENDS",
      "email_confirmed_status"  : "$pending",
      "phone_confirmed_status"  : "$pending",

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    } 
    return self.client.track("$create_account", create_account_properties)

  def create_content_comment(self):
    # Sample $create_content event for comments
    comment_properties = {
      # Required fields
      "$user_id"                : self.user_id,
      "$content_id"             : "comment-23412",

      # Recommended fields
      "$session_id"             : "a234ksjfgn435sfg",
      "$status"                 : "$active",
      "$ip"                     : "255.255.255.0",

      # Required $comment object
      "$comment"                : {
        "$body"               : "Congrats on the new role!",
        "$contact_email"      : "alex_301@domain.com",
        "$parent_comment_id"  : "comment-23407",
        "$root_content_id"    : "listing-12923213",
        "$images"             : [
          {
            "$md5_hash"       : "0cc175b9c0f1b6a831c399e269772661",
            "$link"           : "https://www.domain.com/file.png",
            "$description"    : "An old picture"
          }
        ]
      },
      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$create_content", comment_properties)

  def create_content_listing(self):
    # Sample $create_content event for listings
    listing_properties = {
      # Required fields
      "$user_id"                : self.user_id,
      "$content_id"             : "listing-23412",

      # Recommended fields
      "$session_id"             : "a234ksjfgn435sfg",
      "$status"                 : "$active",
      "$ip"                     : "255.255.255.0",

      # Required $listing object
      "$listing"                : {
        "$subject"            : "2 Bedroom Apartment for Rent",
        "$body"               : "Capitol Hill Seattle brand new condo. 2 bedrooms and 1 full bath.",
        "$contact_email"      : "alex_301@domain.com",
        "$contact_address"    : {
          "$name"           : "Bill Jones",
          "$phone"          : "1-415-555-6041",
          "$city"           : "New London",
          "$region"         : "New Hampshire",
          "$country"        : "US",
          "$zipcode"        : "03257"
        },
        "$locations"          : [
          {
            "$city"           : "Seattle",
            "$region"         : "Washington",
            "$country"        : "US",
            "$zipcode"        : "98112"
          }
        ],
        "$listed_items"       : [
          {
            "$price"          : 2950000000, # $2950.00
            "$currency_code"  : "USD",
            "$tags"           : ["heat", "washer/dryer"]
          }
        ],
        "$images"             : [
          {
            "$md5_hash"       : "0cc175b9c0f1b6a831c399e269772661",
            "$link"           : "https://www.domain.com/file.png",
            "$description"    : "Billy's picture"
          }
        ],
        "$expiration_time"    : 1549063157000 # UNIX timestamp in milliseconds
      },

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$create_content", listing_properties)

  def create_content_message(self):
    # Sample $create_content event for messages
    message_properties = {
        # Required fields
        "$user_id"                 : self.user_id,
        "$content_id"              : "message-23412",

        # Recommended fields
        "$session_id"              : "a234ksjfgn435sfg",
        "$status"                  : "$active",
        "$ip"                      : "255.255.255.0",

        # Required $message object
        "$message"                 : {
          "$body"                : "Let’s meet at 5pm",
          "$contact_email"       : "alex_301@domain.com",
          "$recipient_user_ids"  : ["fy9h989sjphh71"],
          "$images"              : [
            {
              "$md5_hash"        : "0cc175b9c0f1b6a831c399e269772661",
              "$link"            : "https://www.domain.com/file.png",
              "$description"     : "My hike today!"
            }
          ]
        },

        # Send this information from a BROWSER client.
        "$browser"      : {
          "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
          "$accept_language"  : "en-US",
          "$content_language" : "en-GB"
        }
    }
    return self.client.track("$create_content", message_properties)

  def create_content_post(self):
    # Sample $create_content event for posts
    post_properties = {
      # Required fields
      "$user_id"              : self.user_id,
      "$content_id"           : "post-23412",

      # Recommended fields
      "$session_id"           : "a234ksjfgn435sfg",
      "$status"               : "$active",
      "$ip"                   : "255.255.255.0",

      # Required $post object
      "$post"                 : {
        "$subject"          : "My new apartment!",
        "$body"             : "Moved into my new apartment yesterday.",
        "$contact_email"    : "alex_301@domain.com",
        "$contact_address"  : {
          "$name"         : "Bill Jones",
          "$city"         : "New London",
          "$region"       : "New Hampshire",
          "$country"      : "US",
          "$zipcode"      : "03257"
        },
        "$locations"        : [
          {
            "$city"         : "Seattle",
            "$region"       : "Washington",
            "$country"      : "US",
            "$zipcode"      : "98112"
          }
        ],
        "$categories"       : ["Personal"],
        "$images"           : [
          {
            "$md5_hash"     : "0cc175b9c0f1b6a831c399e269772661",
            "$link"         : "https://www.domain.com/file.png",
            "$description"  : "View from the window!"
          }
        ],
        "$expiration_time"  : 1549063157000 # UNIX timestamp in milliseconds
      },

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$create_content", post_properties)

  def create_content_profile(self):
    # Sample $create_content event for reviews
    profile_properties = {
      # Required fields
      "$user_id"              : self.user_id,
      "$content_id"           : "profile-23412",

      # Recommended fields
      "$session_id"           : "a234ksjfgn435sfg",
      "$status"               : "$active",
      "$ip"                   : "255.255.255.0",

      # Required $profile object
      "$profile"              : {
        "$body"             : "Hi! My name is Alex and I just moved to New London!",
        "$contact_email"    : "alex_301@domain.com",
        "$contact_address"  : {
          "$name"         : "Alex Smith",
          "$phone"        : "1-415-555-6041",
          "$city"         : "New London",
          "$region"       : "New Hampshire",
          "$country"      : "US",
          "$zipcode"      : "03257"
        },
        "$images"           : [
          {
            "$md5_hash"     : "0cc175b9c0f1b6a831c399e269772661",
            "$link"         : "https://www.domain.com/file.png",
            "$description"  : "Alex's picture"
          }
        ],
        "$categories"       : [
          "Friends",
          "Long-term dating"
        ]
      },

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$create_content", profile_properties)

  def create_content_review(self):
    # Sample $create_content event for reviews
    review_properties = {
      # Required fields
      "$user_id"                  : self.user_id,
      "$content_id"               : "review-23412",

      # Recommended fields
      "$session_id"               : "a234ksjfgn435sfg",
      "$status"                   : "$active",
      "$ip"                       : "255.255.255.0",

      # Required $review object
      "$review"                   : {
        "$subject"              : "Amazing Tacos!",
        "$body"                 : "I ate the tacos.",
        "$contact_email"        : "alex_301@domain.com",
        "$locations"            : [
          {
            "$city"             : "Seattle",
            "$region"           : "Washington",
            "$country"          : "US",
            "$zipcode"          : "98112"
          }
        ],
        "$reviewed_content_id"  : "listing-234234",
        "$images"               : [
          {
            "$md5_hash"         : "0cc175b9c0f1b6a831c399e269772661",
            "$link"             : "https://www.domain.com/file.png",
            "$description"      : "Calamari tacos."
          }
        ],
        "$rating" : 4.5
      },

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$create_content", review_properties)

  def create_order(self):
    # Sample $create_order event
    order_properties = self.build_create_order_event()
    return self.client.track("$create_order", order_properties)

  def create_order_with_warnings(self):
    # Sample $create_order event
    order_properties = self.build_create_order_event()
    return self.client.track("$create_order", order_properties, include_warnings=True)

  def build_create_order_event(self):
    order_properties = {
      # Required Fields
      "$user_id": self.user_id,
      # Supported Fields
      "$session_id": "gigtleqddo84l8cm15qe4il",
      "$order_id": "ORDER-28168441",
      "$user_email": self.user_email,
      "$verification_phone_number": "+123456789012",
      "$amount": 115940000,  # $115.94
      "$currency_code": "USD",
      "$billing_address": {
        "$name": "Bill Jones",
        "$phone": "1-415-555-6041",
        "$address_1": "2100 Main Street",
        "$address_2": "Apt 3B",
        "$city": "New London",
        "$region": "New Hampshire",
        "$country": "US",
        "$zipcode": "03257"
      },
      "$payment_methods": [
        {
          "$payment_type": "$credit_card",
          "$payment_gateway": "$braintree",
          "$card_bin": "542486",
          "$card_last4": "4444"
        }
      ],
      "$ordered_from": {
        "$store_id": "123",
        "$store_address": {
          "$name": "Bill Jones",
          "$phone": "1-415-555-6040",
          "$address_1": "2100 Main Street",
          "$address_2": "Apt 3B",
          "$city": "New London",
          "$region": "New Hampshire",
          "$country": "US",
          "$zipcode": "03257"
        }
      },
      "$brand_name": "sift",
      "$site_domain": "sift.com",
      "$site_country": "US",
      "$shipping_address": {
        "$name": "Bill Jones",
        "$phone": "1-415-555-6041",
        "$address_1": "2100 Main Street",
        "$address_2": "Apt 3B",
        "$city": "New London",
        "$region": "New Hampshire",
        "$country": "US",
        "$zipcode": "03257"
      },
      "$expedited_shipping": True,
      "$shipping_method": "$physical",
      "$shipping_carrier": "UPS",
      "$shipping_tracking_numbers": ["1Z204E380338943508", "1Z204E380338943509"],
      "$items": [
        {
          "$item_id": "12344321",
          "$product_title": "Microwavable Kettle Corn: Original Flavor",
          "$price": 4990000,  # $4.99
          "$upc": "097564307560",
          "$sku": "03586005",
          "$brand": "Peters Kettle Corn",
          "$manufacturer": "Peters Kettle Corn",
          "$category": "Food and Grocery",
          "$tags": ["Popcorn", "Snacks", "On Sale"],
          "$quantity": 4
        },
        {
          "$item_id": "B004834GQO",
          "$product_title": "The Slanket Blanket-Texas Tea",
          "$price": 39990000,  # $39.99
          "$upc": "6786211451001",
          "$sku": "004834GQ",
          "$brand": "Slanket",
          "$manufacturer": "Slanket",
          "$category": "Blankets & Throws",
          "$tags": ["Awesome", "Wintertime specials"],
          "$color": "Texas Tea",
          "$quantity": 2
        }
      ],
      # For marketplaces, use $seller_user_id to identify the seller
      "$seller_user_id": "slinkys_emporium",

      "$promotions": [
        {
          "$promotion_id": "FirstTimeBuyer",
          "$status": "$success",
          "$description": "$5 off",
          "$discount": {
            "$amount": 5000000,  # $5.00
            "$currency_code": "USD",
            "$minimum_purchase_amount": 25000000  # $25.00
          }
        }
      ],

      # Sample Custom Fields
      "digital_wallet": "apple_pay",  # "google_wallet", etc.
      "coupon_code": "dollarMadness",
      "shipping_choice": "FedEx Ground Courier",
      "is_first_time_buyer": False,

      # Send this information from a BROWSER client.
      "$browser": {
        "$user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language": "en-US",
        "$content_language": "en-GB"
      }
    }
    return order_properties

  def flag_content(self):
    # Sample $flag_content event
    flag_content_properties = {
      # Required Fields
      "$user_id"    : self.user_id, # content creator
      "$content_id" : "9671500641",

      # Supported Fields
      "$flagged_by" : "jamieli89"
    }
    return self.client.track("$flag_content", flag_content_properties)
      
  def link_session_to_user(self):
    # Sample $link_session_to_user event
    link_session_to_user_properties = {
      # Required Fields
      "$user_id"    : self.user_id,
      "$session_id" : "gigtleqddo84l8cm15qe4il"
    }
    return self.client.track("$link_session_to_user", link_session_to_user_properties)

  def login(self):
    # Sample $login event
    login_properties = {
      # Required Fields
      "$user_id"      : self.user_id,
      "$login_status" : "$failure",
      "$session_id"   : "gigtleqddo84l8cm15qe4il",
      "$ip"           : "128.148.1.135",

      # Optional Fields
      "$user_email"                : self.user_email,
      "$verification_phone_number" : "+123456789012",
      "$failure_reason"            : "$wrong_password",
      "$username"                  : "billjones1@example.com",
      "$account_types"             : ["merchant", "premium"],
      "$social_sign_on_type"       : "$linkedin",
      "$brand_name"                : "sift",
      "$site_domain"               : "sift.com",
      "$site_country"              : "US",

      # Send this information with a login from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$login", login_properties)

  def logout(self):
    # Sample $logout event
    logout_properties = {
      # Required Fields
      "$user_id"   : self.user_id,

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$logout", logout_properties)

  def order_status(self):
    # Sample $order_status event
    order_properties = {
      # Required Fields
      "$user_id"          : self.user_id,
      "$order_id"         : "ORDER-28168441",
      "$order_status"     : "$canceled",

      # Optional Fields
      "$reason"           : "$payment_risk",
      "$source"           : "$manual_review",
      "$analyst"          : "someone@your-site.com",
      "$webhook_id"       : "3ff1082a4aea8d0c58e3643ddb7a5bb87ffffeb2492dca33",
      "$description"      : "Canceling because multiple fraudulent users on device",

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }
    return self.client.track("$order_status", order_properties)
      
  def remove_item_from_cart(self):
    # Sample $remove_item_from_cart event
    remove_item_from_cart_properties = {
      # Required Fields
      "$user_id"    : self.user_id,

      # Supported Fields
      "$session_id" : "gigtleqddo84l8cm15qe4il",
      "$item"       : {
        "$item_id"        : "B004834GQO",
        "$product_title"  : "The Slanket Blanket-Texas Tea",
        "$price"          : 39990000, # $39.99
        "$currency_code"  : "USD",
        "$quantity"       : 2,
        "$upc"            : "6786211451001",
        "$sku"            : "004834GQ",
        "$brand"          : "Slanket",
        "$manufacturer"   : "Slanket",
        "$category"       : "Blankets & Throws",
        "$tags"           : ["Awesome", "Wintertime specials"],
        "$color"          : "Texas Tea"
      },
      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }

    return self.client.track("$remove_item_from_cart", remove_item_from_cart_properties)
      
  def security_notification(self):
    # Sample $security_notification event
    security_notification_properties = {
      # Required Fields
      "$user_id"    : self.user_id,
      "$session_id" : "gigtleqddo84l8cm15qe4il",
      "$notification_status"     : "$sent",
      # Optional fields if applicable
      "$notification_type" : "$email",
      "$notified_value"    : "billy123@domain.com",
      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }

    return self.client.track("$security_notification", security_notification_properties)

  def transaction(self):
    # Sample $transaction event
    transaction_properties = {
      # Required Fields
      "$user_id"          : self.user_id,
      "$amount"           : 506790000, # $506.79
      "$currency_code"    : "USD",
      # Supported Fields
      "$user_email"                : self.user_email,
      "$verification_phone_number" : "+123456789012",
      "$transaction_type"          : "$sale",
      "$transaction_status"        : "$failure",
      "$decline_category"          : "$bank_decline",
      "$order_id"                  : "ORDER-123124124",
      "$transaction_id"            : "719637215",
      "$billing_address"  : { # or "$sent_address" # or "$received_address"
        "$name"         : "Bill Jones",
        "$phone"        : "1-415-555-6041",
        "$address_1"    : "2100 Main Street",
        "$address_2"    : "Apt 3B",
        "$city"         : "New London",
        "$region"       : "New Hampshire",
        "$country"      : "US",
        "$zipcode"      : "03257"
      },
      "$brand_name"   : "sift",
      "$site_domain"  : "sift.com",
      "$site_country" : "US",
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
      # Credit card example
      "$payment_method"   : {
          "$payment_type"    : "$credit_card",
          "$payment_gateway" : "$braintree",
          "$card_bin"        : "542486",
          "$card_last4"      : "4444"
      },
      
      # Supported fields for 3DS
      "$status_3ds"                     : "$attempted",
      "$triggered_3ds"                  : "$processor",
      "$merchant_initiated_transaction" : False,

      # Supported Fields
      "$shipping_address" : {
        "$name"         : "Bill Jones",
        "$phone"        : "1-415-555-6041",
        "$address_1"    : "2100 Main Street",
        "$address_2"    : "Apt 3B",
        "$city"         : "New London",
        "$region"       : "New Hampshire",
        "$country"      : "US",
        "$zipcode"      : "03257"
      },
      "$session_id"       : "gigtleqddo84l8cm15qe4il",

      # For marketplaces, use $seller_user_id to identify the seller
      "$seller_user_id"     : "slinkys_emporium",

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
    return self.client.track("$transaction", transaction_properties)
    
  def update_account(self):
    # Sample $update_account event
    update_account_properties = {
      # Required Fields
      "$user_id"    : self.user_id,

      # Supported Fields
      "$changed_password"          : True,
      "$user_email"                : self.user_email,
      "$verification_phone_number" : "+123456789012",
      "$name"                      : "Bill Jones",
      "$phone"                     : "1-415-555-6040",
      "$referrer_user_id"          : "janejane102",
      "$payment_methods"  : [
        {
          "$payment_type"    : "$credit_card",
          "$card_bin"        : "542486",
          "$card_last4"      : "4444"
        }
      ],
      "$billing_address"  :
      {
        "$name"         : "Bill Jones",
        "$phone"        : "1-415-555-6041",
        "$address_1"    : "2100 Main Street",
        "$address_2"    : "Apt 3B",
        "$city"         : "New London",
        "$region"       : "New Hampshire",
        "$country"      : "US",
        "$zipcode"      : "03257"
      },
      "$shipping_address" : {
        "$name"         : "Bill Jones",
        "$phone"        : "1-415-555-6041",
        "$address_1"    : "2100 Main Street",
        "$address_2"    : "Apt 3B",
        "$city"         : "New London",
        "$region"       : "New Hampshire",
        "$country"      : "US",
        "$zipcode"      : "03257"
      },

      "$social_sign_on_type"   : "$twitter",
      "$account_types"          : ["merchant", "premium"],

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }

    return self.client.track("$update_account", update_account_properties)
      
  def update_content_comment(self):
  # Sample $update_content event for comments
    update_content_comment_properties = {
      # Required fields
      "$user_id"                : self.user_id,
      "$content_id"             : "comment-23412",

      # Recommended fields
      "$session_id"             : "a234ksjfgn435sfg",
      "$status"                 : "$active",
      "$ip"                     : "255.255.255.0",

      # Required $comment object
      "$comment"                : {
        "$body"               : "Congrats on the new role!",
        "$contact_email"      : "alex_301@domain.com",
        "$parent_comment_id"  : "comment-23407",
        "$root_content_id"    : "listing-12923213",
        "$images"             : [
          {
            "$md5_hash"       : "0cc175b9c0f1b6a831c399e269772661",
            "$link"           : "https://www.domain.com/file.png",
            "$description"    : "An old picture"
          }
        ]
      },
      # Send this information from an APP client.
      "$app"        : {
        # Example for the iOS Calculator app.
        "$os"                  : "iOS",
        "$os_version"          : "10.1.3",
        "$device_manufacturer" : "Apple",
        "$device_model"        : "iPhone 4,2",
        "$device_unique_id"    : "A3D261E4-DE0A-470B-9E4A-720F3D3D22E6",
        "$app_name"            : "Calculator",
        "$app_version"         : "3.2.7",
        "$client_language"     : "en-US"
      }
    } 
    return self.client.track("$update_content", update_content_comment_properties)
      
  def update_content_listing(self):
    # Sample $update_content event for listings
    update_content_listing_properties = {
      # Required fields
      "$user_id"                : self.user_id,
      "$content_id"             : "listing-23412",

      # Recommended fields
      "$session_id"             : "a234ksjfgn435sfg",
      "$status"                 : "$active",
      "$ip"                     : "255.255.255.0",

      # Required $listing object
      "$listing"                : {
        "$subject"            : "2 Bedroom Apartment for Rent",
        "$body"               : "Capitol Hill Seattle brand new condo. 2 bedrooms and 1 full bath.",
        "$contact_email"      : "alex_301@domain.com",
        "$contact_address"    : {
          "$name"           : "Bill Jones",
          "$phone"          : "1-415-555-6041",
          "$city"           : "New London",
          "$region"         : "New Hampshire",
          "$country"        : "US",
          "$zipcode"        : "03257"
        },
        "$locations"          : [
          {
            "$city"           : "Seattle",
            "$region"         : "Washington",
            "$country"        : "US",
            "$zipcode"        : "98112"
          }
        ],
        "$listed_items"       : [
          {
            "$price"          : 2950000000, # $2950.00
            "$currency_code"  : "USD",
            "$tags"           : ["heat", "washer/dryer"]
          }
        ],
        "$images"             : [
          {
            "$md5_hash"       : "0cc175b9c0f1b6a831c399e269772661",
            "$link"           : "https://www.domain.com/file.png",
            "$description"    : "Billy's picture"
          }
        ],
        "$expiration_time"    : 1549063157000 # UNIX timestamp in milliseconds
      },
      # Send this information from an APP client.
      "$app"        : {
        # Example for the iOS Calculator app.
        "$os"                  : "iOS",
        "$os_version"          : "10.1.3",
        "$device_manufacturer" : "Apple",
        "$device_model"        : "iPhone 4,2",
        "$device_unique_id"    : "A3D261E4-DE0A-470B-9E4A-720F3D3D22E6",
        "$app_name"            : "Calculator",
        "$app_version"         : "3.2.7",
        "$client_language"     : "en-US"
      }
    }
    return self.client.track("$update_content", update_content_listing_properties)
      
  def update_content_message(self):
    # Sample $update_content event for messages
    update_content_message_properties = {
      # Required fields
      "$user_id"                 : self.user_id,
      "$content_id"              : "message-23412",

      # Recommended fields
      "$session_id"              : "a234ksjfgn435sfg",
      "$status"                  : "$active",
      "$ip"                      : "255.255.255.0",

      # Required $message object
      "$message"                 : {
        "$body"                : "Lets meet at 5pm",
        "$contact_email"       : "alex_301@domain.com",
        "$recipient_user_ids"  : ["fy9h989sjphh71"],
        "$images"              : [
          {
            "$md5_hash"        : "0cc175b9c0f1b6a831c399e269772661",
            "$link"            : "https://www.domain.com/file.png",
            "$description"     : "My hike today!"
          }
        ]
      },

      # Send this information from a BROWSER client.
      "$browser"      : {
        "$user_agent" :  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "$accept_language"  : "en-US",
        "$content_language" : "en-GB"
      }
    }

    return self.client.track("$update_content", update_content_message_properties)
      
  def update_content_post(self):
    # Sample $update_content event for posts
    update_content_post_properties = {
      # Required fields
      "$user_id"              : self.user_id,
      "$content_id"           : "post-23412",

      # Recommended fields
      "$session_id"           : "a234ksjfgn435sfg",
      "$status"               : "$active",
      "$ip"                   : "255.255.255.0",

      # Required $post object
      "$post"                 : {
        "$subject"          : "My new apartment!",
        "$body"             : "Moved into my new apartment yesterday.",
        "$contact_email"    : "alex_301@domain.com",
        "$contact_address"  : {
            "$name"         : "Bill Jones",
            "$city"         : "New London",
            "$region"       : "New Hampshire",
            "$country"      : "US",
            "$zipcode"      : "03257"
        },
        "$locations"        : [
          {
            "$city"         : "Seattle",
            "$region"       : "Washington",
            "$country"      : "US",
            "$zipcode"      : "98112"
          }
        ],
        "$categories"       : ["Personal"],
        "$images"           : [
          {
            "$md5_hash"     : "0cc175b9c0f1b6a831c399e269772661",
            "$link"         : "https://www.domain.com/file.png",
            "$description"  : "View from the window!"
          }
        ],
        "$expiration_time"  : 1549063157000 # UNIX timestamp in milliseconds
      },
      # Send this information from an APP client.
      "$app"        : {
        # Example for the iOS Calculator app.
        "$os"                  : "iOS",
        "$os_version"          : "10.1.3",
        "$device_manufacturer" : "Apple",
        "$device_model"        : "iPhone 4,2",
        "$device_unique_id"    : "A3D261E4-DE0A-470B-9E4A-720F3D3D22E6",
        "$app_name"            : "Calculator",
        "$app_version"         : "3.2.7",
        "$client_language"     : "en-US"
      }
    }
    return self.client.track("$update_content", update_content_post_properties)
  
  def update_content_profile(self):
    # Sample $update_content event for reviews
    update_content_profile_properties = {
      # Required fields
      "$user_id"              : self.user_id,
      "$content_id"           : "profile-23412",

      # Recommended fields
      "$session_id"           : "a234ksjfgn435sfg",
      "$status"               : "$active",
      "$ip"                   : "255.255.255.0",

      # Required $profile object
      "$profile"              : {
        "$body"             : "Hi! My name is Alex and I just moved to New London!",
        "$contact_email"    : "alex_301@domain.com",
        "$contact_address"  : {
          "$name"         : "Alex Smith",
          "$phone"        : "1-415-555-6041",
          "$city"         : "New London",
          "$region"       : "New Hampshire",
          "$country"      : "US",
          "$zipcode"      : "03257"
        },
        "$images"           : [
          {
            "$md5_hash"     : "0cc175b9c0f1b6a831c399e269772661",
            "$link"         : "https://www.domain.com/file.png",
            "$description"  : "Alex's picture"
          }
        ],
        "$categories"       : [
          "Friends",
          "Long-term dating"
        ]
      },
      # =========================================
      # Send this information from an APP client.
      "$app"        : {
        # Example for the iOS Calculator app.
        "$os"                  : "iOS",
        "$os_version"          : "10.1.3",
        "$device_manufacturer" : "Apple",
        "$device_model"        : "iPhone 4,2",
        "$device_unique_id"    : "A3D261E4-DE0A-470B-9E4A-720F3D3D22E6",
        "$app_name"            : "Calculator",
        "$app_version"         : "3.2.7",
        "$client_language"     : "en-US"
      }
    }
    return self.client.track("$update_content", update_content_profile_properties)
      
  def update_content_review(self):
    # Sample $update_content event for reviews
    update_content_review_properties = {
      # Required fields
      "$user_id"                  : self.user_id,
      "$content_id"               : "review-23412",

      # Recommended fields
      "$session_id"               : "a234ksjfgn435sfg",
      "$status"                   : "$active",
      "$ip"                       : "255.255.255.0",

      # Required $review object
      "$review"                   : {
        "$subject"              : "Amazing Tacos!",
        "$body"                 : "I ate the tacos.",
        "$contact_email"        : "alex_301@domain.com",
        "$locations"            : [
          {
            "$city"             : "Seattle",
            "$region"           : "Washington",
            "$country"          : "US",
            "$zipcode"          : "98112"
          }
        ],
        "$reviewed_content_id"  : "listing-234234",
        "$images"               : [
          {
            "$md5_hash"         : "0cc175b9c0f1b6a831c399e269772661",
            "$link"             : "https://www.domain.com/file.png",
            "$description"      : "Calamari tacos."
          }
        ],
        "$rating" : 4.5
      },
      # Send this information from an APP client.
      "$app"        : {
        # Example for the iOS Calculator app.
        "$os"                  : "iOS",
        "$os_version"          : "10.1.3",
        "$device_manufacturer" : "Apple",
        "$device_model"        : "iPhone 4,2",
        "$device_unique_id"    : "A3D261E4-DE0A-470B-9E4A-720F3D3D22E6",
        "$app_name"            : "Calculator",
        "$app_version"         : "3.2.7",
        "$client_language"     : "en-US"
      }
    }
    return self.client.track("$update_content", update_content_review_properties)

  def update_order(self):
    # Sample $update_order event
    update_order_properties = {
      # Required Fields
      "$user_id"          : self.user_id,
      # Supported Fields
      "$session_id"                : "gigtleqddo84l8cm15qe4il",
      "$order_id"                  : "ORDER-28168441",
      "$user_email"                : self.user_email,
      "$verification_phone_number" : "+123456789012",
      "$amount"           : 115940000, # $115.94
      "$currency_code"    : "USD",
      "$billing_address"  : {
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
      "$brand_name"   : "sift",
      "$site_domain"  : "sift.com",
      "$site_country" : "US",
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
      # Send this information from an APP client.
      "$app"        : {
        # Example for the iOS Calculator app.
        "$os"                  : "iOS",
        "$os_version"          : "10.1.3",
        "$device_manufacturer" : "Apple",
        "$device_model"        : "iPhone 4,2",
        "$device_unique_id"    : "A3D261E4-DE0A-470B-9E4A-720F3D3D22E6",
        "$app_name"            : "Calculator",
        "$app_version"         : "3.2.7",
        "$client_language"     : "en-US"
      }
    }
    return self.client.track("$update_order", update_order_properties)

  def update_password(self):
    # Sample $update_password event
    update_password_properties = {
      # Required Fields
      "$user_id"       : self.user_id,
      "$session_id"    : "gigtleqddo84l8cm15qe4il",
      "$status"        : "$success",
      "$reason"        : "$forced_reset",
      "$ip"            : "128.148.1.135",     # IP of the user that entered the new password after the old password was reset
      # Send this information from an APP client.
      "$app"        : {
        # Example for the iOS Calculator app.
        "$os"                  : "iOS",
        "$os_version"          : "10.1.3",
        "$device_manufacturer" : "Apple",
        "$device_model"        : "iPhone 4,2",
        "$device_unique_id"    : "A3D261E4-DE0A-470B-9E4A-720F3D3D22E6",
        "$app_name"            : "Calculator",
        "$app_version"         : "3.2.7",
        "$client_language"     : "en-US"
      }
    }
    return self.client.track("$update_password", update_password_properties)

  def verification(self):
    # Sample $verification event
    verification_properties = {
      # Required Fields
      "$user_id"            : self.user_id,
      "$session_id"         : "gigtleqddo84l8cm15qe4il",
      "$status"             : "$pending",

      # Optional fields if applicable
      "$verified_event"     : "$login",
      "$reason"             : "$automated_rule", 
      "$verification_type"  : "$sms",
      "$verified_value"     : "14155551212"
    }
    return self.client.track("$verification", verification_properties)
  