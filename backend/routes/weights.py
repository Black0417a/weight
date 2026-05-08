from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import WeightRecord, UserGoal, RewardRule, UserReward
from datetime import datetime, date, timedelta
import json

weights_bp = Blueprint('weights', __name__)


def check_goal_achievement(user_id, current_weight):
    goal = UserGoal.query.filter_by(user_id=user_id).first()
    if not goal:
        return None

    if current_weight > goal.target_weight:
        return None

    active_rules = RewardRule.query.filter_by(
        condition_type='goal_achievement',
        is_active=True
    ).all()

    rewards = []
    for rule in active_rules:
        target_users = json.loads(rule.target_users) if rule.target_users else 'all'
        if target_users != 'all':
            if str(user_id) not in [str(u) for u in target_users]:
                continue

        params = json.loads(rule.condition_params) if rule.condition_params else {}
        required_percentage = float(params.get('percentage', 100))

        if required_percentage > 100:
            continue

        existing = UserReward.query.filter_by(
            user_id=user_id,
            rule_id=rule.id
        ).first()
        if existing:
            continue

        reward = UserReward(
            user_id=user_id,
            rule_id=rule.id,
            reward_type=rule.reward_type,
            reward_content=rule.reward_content,
            reward_image=rule.reward_image,
            weight_value=current_weight,
            target_weight=goal.target_weight,
            is_read=False
        )
        db.session.add(reward)
        rewards.append(reward)

    if rewards:
        db.session.flush()

    return [r.to_dict() for r in rewards] if rewards else None


def check_weight_change(user_id, current_weight, record_date):
    active_rules = RewardRule.query.filter_by(
        condition_type='weight_change',
        is_active=True
    ).all()

    if not active_rules:
        return None

    rewards = []
    for rule in active_rules:
        target_users = json.loads(rule.target_users) if rule.target_users else 'all'
        if target_users != 'all':
            if str(user_id) not in [str(u) for u in target_users]:
                continue

        params = json.loads(rule.condition_params) if rule.condition_params else {}
        days = int(params.get('days', 7))
        weight_kg = float(params.get('weight_kg', 2))

        if days <= 0 or weight_kg <= 0:
            continue

        lookback_date = record_date - timedelta(days=days)
        old_records = WeightRecord.query.filter(
            WeightRecord.user_id == user_id,
            WeightRecord.record_date >= lookback_date,
            WeightRecord.record_date < record_date
        ).order_by(WeightRecord.record_date.asc()).all()

        if not old_records:
            continue

        oldest_weight = old_records[0].weight
        decrease = oldest_weight - current_weight

        if decrease < weight_kg:
            continue

        existing = UserReward.query.filter_by(
            user_id=user_id,
            rule_id=rule.id,
            weight_value=current_weight
        ).first()
        if existing:
            continue

        reward = UserReward(
            user_id=user_id,
            rule_id=rule.id,
            reward_type=rule.reward_type,
            reward_content=rule.reward_content,
            reward_image=rule.reward_image,
            weight_value=current_weight,
            target_weight=decrease,
            is_read=False
        )
        db.session.add(reward)
        rewards.append(reward)

    if rewards:
        db.session.flush()

    return [r.to_dict() for r in rewards] if rewards else None


@weights_bp.route('/weights', methods=['GET'])
@jwt_required()
def get_weights():
    user_id = int(get_jwt_identity())
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = WeightRecord.query.filter_by(user_id=user_id)

    if start_date:
        query = query.filter(WeightRecord.record_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(WeightRecord.record_date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    records = query.order_by(WeightRecord.record_date.asc()).all()
    return jsonify([r.to_dict() for r in records]), 200


@weights_bp.route('/weights', methods=['POST'])
@jwt_required()
def create_weight():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('weight') or not data.get('record_date'):
        return jsonify({'error': '体重和日期不能为空'}), 400

    weight = float(data['weight'])
    if weight <= 0 or weight > 500:
        return jsonify({'error': '体重数值不合法，应为1-500之间的数值'}), 400

    try:
        record_date = datetime.strptime(data['record_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式不正确，应为YYYY-MM-DD'}), 400

    if record_date > date.today():
        return jsonify({'error': '不能选择未来日期'}), 400

    existing = WeightRecord.query.filter_by(user_id=user_id, record_date=record_date).first()
    if existing:
        existing.weight = weight
        db.session.commit()
        goal_rewards = check_goal_achievement(user_id, weight)
        change_rewards = check_weight_change(user_id, weight, record_date)
        combined = (goal_rewards or []) + (change_rewards or [])
        db.session.commit()
        return jsonify({
            'message': '体重记录已更新',
            'record': existing.to_dict(),
            'rewards': combined if combined else None
        }), 200

    record = WeightRecord(user_id=user_id, weight=weight, record_date=record_date)
    db.session.add(record)
    db.session.commit()
    goal_rewards = check_goal_achievement(user_id, weight)
    change_rewards = check_weight_change(user_id, weight, record_date)
    combined = (goal_rewards or []) + (change_rewards or [])
    db.session.commit()
    return jsonify({
        'message': '体重记录已保存',
        'record': record.to_dict(),
        'rewards': combined if combined else None
    }), 201


@weights_bp.route('/weights/batch', methods=['POST'])
@jwt_required()
def batch_create_weights():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not isinstance(data.get('records'), list):
        return jsonify({'error': '请提供有效的记录列表'}), 400

    records_data = data['records']
    if len(records_data) == 0:
        return jsonify({'error': '记录列表不能为空'}), 400

    saved_count = 0
    for item in records_data:
        try:
            weight = float(item.get('weight', 0))
            if weight <= 0 or weight > 500:
                continue
            record_date = datetime.strptime(item['record_date'], '%Y-%m-%d').date()
            if record_date > date.today():
                continue

            existing = WeightRecord.query.filter_by(user_id=user_id, record_date=record_date).first()
            if existing:
                existing.weight = weight
            else:
                record = WeightRecord(user_id=user_id, weight=weight, record_date=record_date)
                db.session.add(record)
            saved_count += 1
        except (ValueError, KeyError):
            continue

    db.session.commit()
    return jsonify({'message': f'成功保存 {saved_count} 条记录', 'count': saved_count}), 200


@weights_bp.route('/weights/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_weight(record_id):
    user_id = int(get_jwt_identity())
    record = WeightRecord.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        return jsonify({'error': '记录不存在'}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '记录已删除'}), 200


@weights_bp.route('/rewards', methods=['GET'])
@jwt_required()
def get_rewards():
    user_id = int(get_jwt_identity())
    rewards = UserReward.query.filter_by(user_id=user_id).order_by(UserReward.created_at.desc()).all()
    return jsonify([r.to_dict() for r in rewards]), 200


@weights_bp.route('/rewards/unread-count', methods=['GET'])
@jwt_required()
def get_unread_reward_count():
    user_id = int(get_jwt_identity())
    count = UserReward.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({'count': count}), 200


@weights_bp.route('/rewards/<int:reward_id>/read', methods=['PUT'])
@jwt_required()
def mark_reward_read(reward_id):
    user_id = int(get_jwt_identity())
    reward = UserReward.query.filter_by(id=reward_id, user_id=user_id).first()
    if not reward:
        return jsonify({'error': '奖励不存在'}), 404

    reward.is_read = True
    db.session.commit()
    return jsonify({'message': '已标记为已读'}), 200
