from flask import jsonify, request
from app import app
from app.services.recomendation_service import generate_recommendations
from app.services.customer_service import fetch_customers
from app.services.demand_prediction import predict_next_month_sales


@app.route('/product/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    num_recommendations = request.args.get('num', 5, type=int)
    try:
        # Generar recomendaciones (obtenemos los IDs de los productos)
        #recommended_products = generate_recommendations(user_id, num_recommendations)
        recommendations = generate_recommendations(user_id, num_recommendations)
        # Estructurar las recomendaciones en el formato deseado
        formatted_recommendations = [
            {
                "id": rec["id"],
                "category": {
                    "id": rec["cat_id"],
                    "catName": "Nombre de la categoría",  # Este valor debería obtenerse desde la base de datos
                    "catDescription": "Descripción de la categoría",  # Este valor debería obtenerse desde la base de datos
                    "catStatus": bool(rec["pro_status"]),
                    "catHasTaco": True  # Este valor también debería obtenerse desde la base de datos
                },
                "proName": rec["pro_name"],
                "proDescription": rec["pro_description"],
                "proUnitPrice": rec["pro_unit_price"],
                "proUnitCost": rec["pro_unit_cost"],
                "proSize": rec["pro_size"],
                "proSizePlatform": rec["pro_size_platform"],
                "proSizeTaco": rec["pro_size_taco"],
                "proUrlImage": rec["pro_url_image"],
                "proColor": rec["pro_color"],
                "proStock": rec["pro_stock"],
                "proStatus": bool(rec["pro_status"])
            }
            for rec in recommendations
        ]

        # Estructurar la respuesta completa
        response = {
            "status": 200,
            "message": "Lista de productos exitosamente",
            "data": {
                "content": formatted_recommendations
            }
        }
        return jsonify(response)
        #return jsonify({"user_id": user_id, "recommendations": recommendations_list})
    except ValueError as e:
        print(f"ValueError: {e}")  # Imprimir error para depuración
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")  # Imprimir error inesperado
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route('/customers', methods=['GET'])
def list_customers():
    print("Ruta /customers fue llamada")  # Depuración
    try:
        customers = fetch_customers()
        return jsonify({"customers": customers})
    except Exception as e:
        print(f"Error: {e}")  # Depuración
        return jsonify({"error": str(e)}), 500

@app.route('/product/demanding', methods=['POST'])
def get_product_demand():
    try:
        # Obtener los datos del JSON de la solicitud
        data = request.get_json()

        # Validar los datos
        product_id = data.get('product_id')
        year = data.get('year')
        month = data.get('month')

        if product_id is None or year is None or month is None:
            return jsonify({'error': 'Faltan parámetros en la solicitud'}), 400

        # Llamar a la función de predicción
        prediction = predict_next_month_sales(product_id, year, month)

        # Devolver la predicción como JSON
        return jsonify({'product_id': product_id, 'prediction': prediction})

    except Exception as e:
        return jsonify({'error': str(e)}), 500