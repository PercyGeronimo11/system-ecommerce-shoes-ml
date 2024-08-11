from app.models.db_models import fetch_data

def get_all_orders():
    query = "SELECT * FROM orders"
    return fetch_data(query)

def get_order_by_id(order_id):
    query = "SELECT * FROM orders WHERE ord_id = %s"
    return fetch_data(query, (order_id,))

