from app.models.db_models import fetch_data

def get_all_order_details():
    query = "SELECT * FROM order_detail"
    return fetch_data(query)

def get_order_detail_by_id(order_id, product_id):
    query = "SELECT * FROM order_detail WHERE ord_id = %s AND id = %s"
    return fetch_data(query, (order_id, product_id))
