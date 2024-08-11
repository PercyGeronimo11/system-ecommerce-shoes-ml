from app.models.db_models import fetch_data

def get_all_products():
    query = "SELECT * FROM product"
    return fetch_data(query)

def get_product_by_id(product_id):
    query = "SELECT * FROM product WHERE id = %s"
    return fetch_data(query, (product_id,))