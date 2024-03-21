import stripe
from woocommerce import API

# Stripe setup
stripe.api_key = 'YOUR_STRIPE_SECRET_KEY'

# WooCommerce setup
wc_api = API(
    url="YOUR_WOOCOMMERCE_SITE_URL",
    consumer_key="YOUR_CONSUMER_KEY",
    consumer_secret="YOUR_CONSUMER_SECRET",
    version="wc/v3"
)


def fetch_stripe_customers():
    stripe_customers = []
    last_customer_id = None

    while True:
        params = {'limit': 100}
        if last_customer_id:
            params['starting_after'] = last_customer_id

        response = stripe.Customer.list(**params)
        if not response.data:
            break

        stripe_customers.extend(response.data)
        last_customer_id = response.data[-1].id

    return stripe_customers


def find_woocommerce_user_id_by_email(email):
    response = wc_api.get("customers", params={"email": email}).json()
    if response:
        return response[0]['id']
    return None


def add_or_update_woocommerce_customer(customer):
    user_id = find_woocommerce_user_id_by_email(customer.email)
    customer_data = {
        'email': customer.email,
        'first_name': customer.name,
        'username': customer.email.split('@')[0],  # Example username creation
    }

    if user_id:
        # Update existing user
        response = wc_api.put(f"customers/{user_id}", customer_data).json()
    else:
        # Create new user
        response = wc_api.post("customers", customer_data).json()

    return response


def process_customers():
    customers = fetch_stripe_customers()
    for customer in customers:
        result = add_or_update_woocommerce_customer(customer)
        print(f"Processed customer: {result.get('id', 'Unknown ID')} - {result.get('email', 'No email')}")

if __name__ == "__main__":
    process_customers()

