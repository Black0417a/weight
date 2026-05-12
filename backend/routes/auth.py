from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import User, UserReminderSetting
from datetime import datetime, timedelta
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


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供更新数据'}), 400

    if 'height' in data:
        height = data['height']
        if height is not None and height != '':
            height = float(height)
            if height <= 0 or height > 300:
                return jsonify({'error': '身高数值不合法，应为1-300cm'}), 400
            user.height = height
        else:
            user.height = None

    if 'birthday' in data:
        birthday = data['birthday']
        if birthday is not None and birthday != '':
            try:
                user.birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '生日格式不正确，应为YYYY-MM-DD'}), 400
        else:
            user.birthday = None

    db.session.commit()
    return jsonify({'message': '个人资料已更新', 'user': user.to_dict()}), 200
