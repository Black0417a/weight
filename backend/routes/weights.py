from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import WeightRecord
from datetime import datetime, date

weights_bp = Blueprint('weights', __name__)


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
        return jsonify({'message': '体重记录已更新', 'record': existing.to_dict()}), 200

    record = WeightRecord(user_id=user_id, weight=weight, record_date=record_date)
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': '体重记录已保存', 'record': record.to_dict()}), 201


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
