import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from app.models.db_models import fetch_data

def get_interaction_data():
    query = '''
        SELECT cp.customerId as userId, cp.productId, cp.clicks, cp.rating, od.quantity
        FROM customer_products cp
        LEFT JOIN orderDetail od ON cp.customerId = od.custId AND cp.productId = od.productId
    '''
    return pd.DataFrame(fetch_data(query))

def train_model():
    interaction_data = get_interaction_data()
    interaction_data = interaction_data.fillna(0)

    interaction_data['interaction'] = interaction_data['clicks'] + interaction_data['rating'] + interaction_data['quantity']
    
    user_product_matrix = interaction_data.pivot_table(index='userId', columns='productId', values='interaction', aggfunc='sum').fillna(0)
    
    svd = TruncatedSVD(n_components=20, random_state=42)
    user_matrix = svd.fit_transform(csr_matrix(user_product_matrix.values))
    product_matrix = svd.components_

    user_similarity = cosine_similarity(user_matrix)
    
    user_similarity_df = pd.DataFrame(user_similarity, index=user_product_matrix.index, columns=user_product_matrix.index)
    
    return user_similarity_df, user_product_matrix

def generate_recommendations(user_id, num_recommendations=5):
    user_similarity_df, user_product_matrix = train_model()
    
    if user_id not in user_similarity_df.index:
        raise ValueError(f"User ID {user_id} not found in user similarity matrix.")
    
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:num_recommendations+1].index
    similar_users_interactions = user_product_matrix.loc[similar_users]

    weighted_interactions = similar_users_interactions.apply(lambda x: np.dot(x, user_similarity_df.loc[user_id, similar_users]), axis=0)
    
    recommendations = weighted_interactions.sort_values(ascending=False).index
    return recommendations.tolist()
