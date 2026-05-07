from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import UserReminderSetting

reminder_bp = Blueprint('reminder', __name__)


@reminder_bp.route('/reminder-settings', methods=['GET'])
@jwt_required()
def get_reminder_settings():
    user_id = int(get_jwt_identity())
    setting = UserReminderSetting.query.filter_by(user_id=user_id).first()

    if not setting:
        setting = UserReminderSetting(user_id=user_id, email_reminder_enabled=True)
        db.session.add(setting)
        db.session.commit()

    return jsonify(setting.to_dict()), 200


@reminder_bp.route('/reminder-settings', methods=['PUT'])
@jwt_required()
def update_reminder_settings():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if 'email_reminder_enabled' not in data:
        return jsonify({'error': 'email_reminder_enabled字段不能为空'}), 400

    setting = UserReminderSetting.query.filter_by(user_id=user_id).first()
    if not setting:
        setting = UserReminderSetting(user_id=user_id, email_reminder_enabled=data['email_reminder_enabled'])
        db.session.add(setting)
    else:
        setting.email_reminder_enabled = data['email_reminder_enabled']

    db.session.commit()
    return jsonify({'message': '提醒设置已更新', 'setting': setting.to_dict()}), 200
