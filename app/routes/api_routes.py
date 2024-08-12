from flask import jsonify, request
from app import app
from app.services.recomendation_service import generate_recommendations
from app.services.customer_service import fetch_customers



@app.route('/product/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    num_recommendations = request.args.get('num', 5, type=int)
    try:
        recommendations = generate_recommendations(user_id, num_recommendations)
        
        # Imprimir para depuración
        print(f"Recommendations for user {user_id}: {recommendations}")

        # Asegúrate de que las recomendaciones sean convertibles a JSON
        recommendations_list = recommendations.tolist() if hasattr(recommendations, 'tolist') else list(recommendations)
        
        return jsonify({"user_id": user_id, "recommendations": recommendations_list})
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
