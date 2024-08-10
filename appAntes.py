from flask import Flask, request, jsonify
import jwt
import mysql.connector
import random

app = Flask(__name__)
SECRET_KEY = 'your_jwt_secret_key'

def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS512'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_db_connection():
    return mysql.connector.connect(
        host="your_db_host",
        user="your_db_user",
        password="your_db_password",
        database="your_db_name"
    )

@app.route('/recomendaciones', methods=['GET'])
def get_recomendaciones():
    token = request.headers.get('Authorization').split(" ")[1]
    user_info = verify_jwt(token)
    if not user_info:
        return jsonify({"message": "Invalid token"}), 401

    user_id = user_info['sub']
    recomendaciones = generate_recommendations(user_id)
    return jsonify(recomendaciones)

def generate_recommendations(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener historial de navegación
    cursor.execute('SELECT product_id FROM historial_navegacion WHERE user_id = %s', (user_id,))
    navegacion = cursor.fetchall()
    
    # Obtener historial de compras
    cursor.execute('SELECT product_id FROM compras WHERE user_id = %s', (user_id,))
    compras = cursor.fetchall()

    # Convertir resultados en una lista de IDs de productos
    productos_navegados = [item[0] for item in navegacion]
    productos_comprados = [item[0] for item in compras]
    
    # Combinar historial de navegación y compras
    historial_total = productos_navegados + productos_comprados
    
    # Si no hay historial, devolver recomendaciones aleatorias
    if not historial_total:
        cursor.execute('SELECT id FROM productos')
        all_products = cursor.fetchall()
        recomendaciones = random.sample([item[0] for item in all_products], 5)
        return recomendaciones
    
    # Generar recomendaciones basadas en historial
    # Para simplicidad, este ejemplo recomienda productos similares (por categoría, etc.)
    cursor.execute('SELECT category_id FROM productos WHERE id IN (%s)' % ','.join(['%s']*len(historial_total)), tuple(historial_total))
    categorias = cursor.fetchall()
    categorias_ids = [item[0] for item in categorias]
    
    cursor.execute('SELECT id FROM productos WHERE category_id IN (%s) AND id NOT IN (%s)' % (','.join(['%s']*len(categorias_ids)), ','.join(['%s']*len(historial_total))), tuple(categorias_ids + historial_total))
    productos_similares = cursor.fetchall()
    
    # Seleccionar algunas recomendaciones de los productos similares
    recomendaciones = random.sample([item[0] for item in productos_similares], min(5, len(productos_similares)))
    
    return recomendaciones

if __name__ == '__main__':
    app.run(debug=True)
