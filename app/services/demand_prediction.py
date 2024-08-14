import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import os
import mysql.connector
from app.models.db_models import fetch_data

# Query para obtener los datos de las tablas "orders" y "order_detail"
query = """
SELECT YEAR(o.ord_date) AS year, MONTH(o.ord_date) AS month, od.id as idProduct, od.odt_amount 
FROM orders o
JOIN order_detail od ON o.ord_id = od.ord_id
"""

data = pd.DataFrame(fetch_data(query))

# Seleccionar las columnas relevantes
columns_to_use = ['year', 'month', 'idProduct', 'odt_amount']
final_dataset = data[columns_to_use].copy()

# Dividir el dataset en conjuntos de entrenamiento y prueba
X = final_dataset[['year', 'month', 'idProduct']]
y = final_dataset['odt_amount']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalizar los datos
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Inicializar el modelo de RandomForestRegressor
model = RandomForestRegressor(n_estimators=100, random_state=42)

# Entrenar el modelo
model.fit(X_train_scaled, y_train)

# Hacer predicciones en el conjunto de prueba
y_pred = model.predict(X_test_scaled)


def predict_next_month_sales(product_id, year, month):
    # Crear un DataFrame con la información del producto para la predicción
    data_example = pd.DataFrame({
        'year': [year],
        'month': [month],
        'idProduct': [product_id],
    })

    # Normalizar los datos del ejemplo
    data_example_scaled = scaler.transform(data_example)

    # Realizar la predicción del total de ventas para el mes siguiente
    prediction = model.predict(data_example_scaled)

    return prediction[0]

# Example
""" product_id = 1
try:
    prediction = predict_next_month_sales(product_id)
    print(f"Predicción del total de ventas para el producto {product_id} en el mes siguiente: {prediction}")
except ValueError as e:
    print(e) """