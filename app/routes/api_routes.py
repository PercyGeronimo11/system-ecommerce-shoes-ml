from flask import jsonify, request
from app import app
from app.services.recomendation_service import generate_recommendations
from app.services.customer_service import fetch_customers

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    num_recommendations = request.args.get('num', 5, type=int)
    try:
        recommendations = generate_recommendations(user_id, num_recommendations)
        return jsonify({"user_id": user_id, "recommendations": recommendations})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/customers', methods=['GET'])
def list_customers():
    print("Ruta /customers fue llamada")  # Depuración
    try:
        customers = fetch_customers()
        return jsonify({"customers": customers})
    except Exception as e:
        print(f"Error: {e}")  # Depuración
        return jsonify({"error": str(e)}), 500
