from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from models import User, UserReminderSetting
from datetime import timedelta
import re

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'error': '请输入邮箱地址'}), 400

    email = data['email'].strip().lower()

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({'error': '邮箱格式不正确'}), 400

    user = User.query.filter_by(email=email).first()
    is_new = False

    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.flush()

        reminder = UserReminderSetting(user_id=user.id, email_reminder_enabled=True)
        db.session.add(reminder)

        db.session.commit()
        is_new = True

    expires = timedelta(days=3650)
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': 'user'},
        expires_delta=expires
    )

    return jsonify({
        'token': access_token,
        'user': user.to_dict(),
        'is_new': is_new,
        'message': '登录成功' + ('，账户已自动创建' if is_new else '，欢迎回来')
    }), 200
