from app.models.db_models import fetch_data

def get_all_customers():
    query = "SELECT * FROM customer"
    return fetch_data(query)

def get_customer_by_id(customer_id):
    query = "SELECT * FROM customer WHERE id = %s"
    return fetch_data(query, (customer_id,))

