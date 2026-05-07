from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import UserGoal

goal_bp = Blueprint('goal', __name__)


@goal_bp.route('/goal', methods=['GET'])
@jwt_required()
def get_goal():
    user_id = int(get_jwt_identity())
    goal = UserGoal.query.filter_by(user_id=user_id).first()

    if not goal:
        return jsonify({'target_weight': None, 'has_goal': False}), 200

    return jsonify(goal.to_dict()), 200


@goal_bp.route('/goal', methods=['PUT'])
@jwt_required()
def set_goal():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('target_weight'):
        return jsonify({'error': '目标体重不能为空'}), 400

    target_weight = float(data['target_weight'])
    if target_weight <= 0 or target_weight > 500:
        return jsonify({'error': '目标体重数值不合法'}), 400

    goal = UserGoal.query.filter_by(user_id=user_id).first()
    if goal:
        goal.target_weight = target_weight
    else:
        goal = UserGoal(user_id=user_id, target_weight=target_weight)
        db.session.add(goal)

    db.session.commit()
    return jsonify({'message': '目标体重已保存', 'goal': goal.to_dict()}), 200
