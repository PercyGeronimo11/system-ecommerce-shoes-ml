import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from app.models.db_models import fetch_data


query_purchases = """
SELECT o.id AS userId, od.id AS productId, SUM(od.odt_amount) AS quantity
FROM orders o
JOIN order_detail od ON o.ord_id = od.ord_id
GROUP BY o.id, od.id
"""

query_users = "SELECT id AS userId, cust_first_name AS userName FROM customer"

query_products = "SELECT id AS productId, pro_name AS productName FROM product"

query_clicks= """
SELECT customer_id AS userId, product_id AS productId, SUM(clicks) AS clicks FROM customer_product
GROUP BY customer_id, product_id
"""
query_rating = """
SELECT customer_id AS userId, product_id AS productId,  AVG(rating) AS rating FROM customer_product
GROUP BY customer_id, product_id
"""

# Obtener datos de la base de datos
clicks = pd.DataFrame(fetch_data(query_clicks))
ratings = pd.DataFrame(fetch_data(query_rating))
purchases = pd.DataFrame(fetch_data(query_purchases))
users = pd.DataFrame(fetch_data(query_users))
products = pd.DataFrame(fetch_data(query_products))

# Agregar clics por usuario y producto
clicks_agg = clicks.groupby(['userId', 'productId']).sum().reset_index()

# Agregar cantidad de compras por usuario y producto
purchases_agg = purchases.groupby(['userId', 'productId']).size().reset_index(name='quantity')

# Combinar clics, calificaciones y cantidad de compras
interaction_data = clicks_agg.merge(ratings, on=['userId', 'productId'], how='outer').fillna(0)
interaction_data = interaction_data.merge(purchases_agg, on=['userId', 'productId'], how='outer').fillna(0)

# Crear una columna de interacción total (clics + calificaciones + cantidad de compras)
interaction_data['clicks'] = interaction_data['clicks'].astype(float)
interaction_data['rating'] = interaction_data['rating'].astype(float)
interaction_data['quantity'] = interaction_data['quantity'].astype(float)
interaction_data['interaction'] = interaction_data['clicks'] + interaction_data['rating'] + interaction_data['quantity']

# Crear la matriz de usuario-producto
user_product_matrix = interaction_data.pivot_table(index='userId', columns='productId', values='interaction', aggfunc='sum').fillna(0)

# Convertir a tipo de dato numérico explícitamente
user_product_matrix = user_product_matrix.astype(np.float32)

# Crear la matriz dispersa
user_product_matrix_sparse = csr_matrix(user_product_matrix.values)

# Verificar si hay valores NaN, infinitos o negativos y reemplazarlos por 0
user_product_matrix_sparse.data = np.nan_to_num(user_product_matrix_sparse.data, nan=0.0, posinf=0.0, neginf=0.0)

# Verificar las dimensiones de la matriz
n_users, n_products = user_product_matrix.shape
print(f'Número de usuarios: {n_users}, Número de productos: {n_products}')

# Verificar si la matriz es válida para la descomposición
if n_products <= 1:
    raise ValueError("La matriz de interacción tiene un número insuficiente de características (productos).")

if np.all(user_product_matrix_sparse.data == 0):
    raise ValueError("La matriz de interacción es completamente cero. No se puede aplicar TruncatedSVD.")

# Aplicar TruncatedSVD para la factorización de matrices (Entrenamiento)
n_components = min(n_users, n_products) - 1  # Ajustar el número de componentes

if n_components <= 0:
    raise ValueError("El número de componentes para TruncatedSVD es inválido.")

# Aplicar TruncatedSVD para la factorización de matrices (Entrenamiento)
svd = TruncatedSVD(n_components=2, random_state=42)
user_matrix = svd.fit_transform(user_product_matrix_sparse)
product_matrix = svd.components_

# Calcular la similitud del coseno entre los usuarios
user_similarity = cosine_similarity(user_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=user_product_matrix.index, columns=user_product_matrix.index)

def get_product_details(product_ids):
    if not product_ids:
        return []
    
    format_strings = ','.join(['%s'] * len(product_ids))
    query = f"SELECT * FROM product WHERE id IN ({format_strings})"
    return fetch_data(query, tuple(product_ids))

# Función para generar recomendaciones
def generate_recommendations(user_id, num_recommendations=9):
    if user_id not in user_similarity_df.index:
        raise ValueError(f"User ID {user_id} not found in user similarity matrix.")

    # Obtener los usuarios similares
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:num_recommendations+1].index

    # Obtener las interacciones de estos usuarios
    similar_users_interactions = user_product_matrix.loc[similar_users]

    # Calcular el puntaje ponderado
    weighted_interactions = similar_users_interactions.apply(lambda x: np.dot(x, user_similarity_df.loc[user_id, similar_users]), axis=0)

    # Ordenar los productos por puntaje ponderado
    recommendations = weighted_interactions.sort_values(ascending=False)

    # Limitar el número de recomendaciones
    #top_recommendations = recommendations.head(num_recommendations).index.tolist()
    
    # Limitar el número de recomendaciones
    top_recommendations_ids = recommendations.head(num_recommendations).index.tolist()

  # Obtener los detalles completos de los productos recomendados
    top_recommendations_details = get_product_details(top_recommendations_ids)

    return top_recommendations_details
