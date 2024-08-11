from flask import Blueprint, request, jsonify
from services.recomendation_service import generate_recommendations

api = Blueprint('api', __name__)

@api.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    try:
        recommendations = generate_recommendations(user_id)
        return jsonify(recommendations), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400