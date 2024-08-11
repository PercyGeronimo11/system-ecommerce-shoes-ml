from flask_mysqldb import MySQL
from flask import current_app

def get_db_connection():
    return MySQL(current_app)

def fetch_data(query, params=None):
    conn = get_db_connection()
    cursor = conn.connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    return result
