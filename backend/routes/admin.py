from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import Admin, User, WeightRecord, RewardRule, SystemConfig, UserReward
from datetime import timedelta
from sqlalchemy.orm import joinedload
import bcrypt
import json
import os
import uuid
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            admin_id = int(get_jwt_identity())
            admin = Admin.query.get(admin_id)
            if not admin or not admin.is_active:
                return jsonify({'error': '无权限访问'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@admin_bp.route('/auth/register', methods=['POST'])
def admin_register():
    if Admin.query.count() > 0:
        return jsonify({'error': '管理员注册已关闭，请联系已有管理员添加账户'}), 403

    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400

    username = data['username'].strip()
    password = data['password']

    if len(username) < 3:
        return jsonify({'error': '用户名至少3个字符'}), 400
    if len(password) < 6:
        return jsonify({'error': '密码至少6个字符'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    admin = Admin(username=username, password_hash=password_hash, is_active=True)
    db.session.add(admin)
    db.session.commit()

    return jsonify({
        'message': '首个管理员注册成功，已自动激活',
        'admin': admin.to_dict()
    }), 201


@admin_bp.route('/auth/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400

    admin = Admin.query.filter_by(username=data['username'].strip()).first()
    if not admin:
        return jsonify({'error': '用户名或密码错误'}), 401

    if not bcrypt.checkpw(data['password'].encode('utf-8'), admin.password_hash.encode('utf-8')):
        return jsonify({'error': '用户名或密码错误'}), 401

    if not admin.is_active:
        return jsonify({'error': '账户尚未激活'}), 403

    expires = timedelta(days=3650)
    access_token = create_access_token(
        identity=str(admin.id),
        additional_claims={'role': 'admin'},
        expires_delta=expires
    )

    return jsonify({'token': access_token, 'admin': admin.to_dict()}), 200


@admin_bp.route('/admins', methods=['GET'])
@admin_required()
def list_admins():
    admins = Admin.query.order_by(Admin.created_at.desc()).all()
    return jsonify([a.to_dict() for a in admins]), 200


@admin_bp.route('/admins', methods=['POST'])
@admin_required()
def create_admin():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400

    username = data['username'].strip()
    password = data['password']

    if len(username) < 3:
        return jsonify({'error': '用户名至少3个字符'}), 400
    if len(password) < 6:
        return jsonify({'error': '密码至少6个字符'}), 400

    if Admin.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin = Admin(username=username, password_hash=password_hash, is_active=True)
    db.session.add(admin)
    db.session.commit()

    return jsonify({'message': '管理员创建成功', 'admin': admin.to_dict()}), 201


@admin_bp.route('/admins/<int:admin_id>', methods=['DELETE'])
@admin_required()
def delete_admin(admin_id):
    current_admin_id = int(get_jwt_identity())
    if admin_id == current_admin_id:
        return jsonify({'error': '不能删除自己'}), 400

    admin = Admin.query.get(admin_id)
    if not admin:
        return jsonify({'error': '管理员不存在'}), 404

    if Admin.query.filter_by(is_active=True).count() <= 1:
        return jsonify({'error': '不能删除最后一个管理员'}), 400

    db.session.delete(admin)
    db.session.commit()
    return jsonify({'message': '管理员已删除'}), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str)

    query = User.query
    if search:
        query = query.filter(User.email.contains(search))

    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required()
def get_user_detail(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    records = WeightRecord.query.filter_by(user_id=user_id).order_by(WeightRecord.record_date.desc()).limit(100).all()

    return jsonify({
        'user': user.to_dict(),
        'weight_records': [r.to_dict() for r in records],
        'record_count': len(records)
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': '用户已删除'}), 200


@admin_bp.route('/reward-rules', methods=['GET'])
@admin_required()
def get_reward_rules():
    rules = RewardRule.query.order_by(RewardRule.created_at.desc()).all()
    return jsonify([r.to_dict() for r in rules]), 200


@admin_bp.route('/reward-rules', methods=['POST'])
@admin_required()
def create_reward_rule():
    data = request.get_json()

    required_fields = ['name', 'condition_type', 'condition_params', 'grant_mode']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field}不能为空'}), 400

    rule = RewardRule(
        name=data['name'],
        condition_type=data['condition_type'],
        condition_params=json.dumps(data['condition_params']),
        reward_type=data.get('reward_type', 'text'),
        reward_content=data.get('reward_content', ''),
        reward_image=data.get('reward_image', None),
        grant_mode=data['grant_mode'],
        target_users=json.dumps(data.get('target_users', 'all')),
        is_active=data.get('is_active', True)
    )
    db.session.add(rule)
    db.session.commit()

    return jsonify({'message': '奖励规则已创建', 'rule': rule.to_dict()}), 201


@admin_bp.route('/reward-rules/<int:rule_id>', methods=['PUT'])
@admin_required()
def update_reward_rule(rule_id):
    rule = RewardRule.query.get(rule_id)
    if not rule:
        return jsonify({'error': '规则不存在'}), 404

    data = request.get_json()

    if data.get('name'):
        rule.name = data['name']
    if data.get('condition_type'):
        rule.condition_type = data['condition_type']
    if data.get('condition_params'):
        rule.condition_params = json.dumps(data['condition_params'])
    if data.get('reward_type'):
        rule.reward_type = data['reward_type']
    if 'reward_content' in data:
        rule.reward_content = data['reward_content']
    if data.get('grant_mode'):
        rule.grant_mode = data['grant_mode']
    if data.get('target_users') is not None:
        rule.target_users = json.dumps(data['target_users'])
    if 'is_active' in data:
        rule.is_active = data['is_active']

    db.session.commit()
    return jsonify({'message': '规则已更新', 'rule': rule.to_dict()}), 200


@admin_bp.route('/reward-rules/<int:rule_id>', methods=['DELETE'])
@admin_required()
def delete_reward_rule(rule_id):
    rule = RewardRule.query.get(rule_id)
    if not rule:
        return jsonify({'error': '规则不存在'}), 404

    db.session.delete(rule)
    db.session.commit()
    return jsonify({'message': '规则已删除'}), 200


@admin_bp.route('/reward-rules/<int:rule_id>/upload-image', methods=['POST'])
@admin_required()
def upload_reward_image(rule_id):
    rule = RewardRule.query.get(rule_id)
    if not rule:
        return jsonify({'error': '规则不存在'}), 404

    if 'image' not in request.files:
        return jsonify({'error': '未上传图片'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        return jsonify({'error': '不支持的图片格式'}), 400

    filename = f'reward_{uuid.uuid4().hex}.{ext}'
    upload_path = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_path, filename)
    file.save(filepath)

    rule.reward_image = f'/api/admin/uploads/{filename}'
    rule.reward_type = 'image'
    db.session.commit()

    return jsonify({'message': '图片上传成功', 'image_url': rule.reward_image}), 200


@admin_bp.route('/uploads/<filename>', methods=['GET'])
def serve_upload(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@admin_bp.route('/configs', methods=['GET'])
@admin_required()
def get_configs():
    configs = SystemConfig.query.all()
    return jsonify([c.to_dict() for c in configs]), 200


@admin_bp.route('/configs/<string:key>', methods=['PUT'])
@admin_required()
def update_config(key):
    config = SystemConfig.query.filter_by(key=key).first()
    if not config:
        return jsonify({'error': '配置项不存在'}), 404

    data = request.get_json()
    if 'value' not in data:
        return jsonify({'error': '值不能为空'}), 400

    config.value = data['value']
    if data.get('description'):
        config.description = data['description']

    db.session.commit()
    return jsonify({'message': '配置已更新', 'config': config.to_dict()}), 200


@admin_bp.route('/reward-push-records', methods=['GET'])
@admin_required()
def get_reward_push_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str)
    filter_rule_id = request.args.get('rule_id', None, type=int)
    filter_read = request.args.get('is_read', None, type=str)
    filter_type = request.args.get('condition_type', '', type=str)

    query = UserReward.query.options(joinedload(UserReward.rule))

    if search:
        query = query.join(User, UserReward.user_id == User.id).filter(
            User.email.contains(search)
        ).reset_joinpoint()

    if filter_rule_id:
        query = query.filter(UserReward.rule_id == filter_rule_id)
    if filter_read == 'read':
        query = query.filter(UserReward.is_read == True)
    elif filter_read == 'unread':
        query = query.filter(UserReward.is_read == False)
    if filter_type:
        query = query.join(RewardRule, UserReward.rule_id == RewardRule.id).filter(
            RewardRule.condition_type == filter_type
        ).reset_joinpoint()

    pagination = query.order_by(UserReward.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    records = []
    user_ids = list(set(r.user_id for r in pagination.items))
    users_map = {u.id: u.email for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}
    for reward in pagination.items:
        item = reward.to_dict()
        item['user_email'] = users_map.get(reward.user_id, '未知用户')
        records.append(item)

    rules = RewardRule.query.all()

    return jsonify({
        'records': records,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'rules': [{'id': r.id, 'name': r.name} for r in rules]
    }), 200


@admin_bp.route('/reward-push-records/stats', methods=['GET'])
@admin_required()
def reward_push_stats():
    total_pushed = UserReward.query.count()
    unread_count = UserReward.query.filter_by(is_read=False).count()
    read_count = UserReward.query.filter_by(is_read=True).count()

    return jsonify({
        'total_pushed': total_pushed,
        'unread_count': unread_count,
        'read_count': read_count
    }), 200


@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required()
def dashboard_stats():
    user_count = User.query.count()
    record_count = WeightRecord.query.count()
    active_rule_count = RewardRule.query.filter_by(is_active=True).count()
    reward_count = UserReward.query.count()

    return jsonify({
        'user_count': user_count,
        'record_count': record_count,
        'active_rule_count': active_rule_count,
        'reward_count': reward_count,
    }), 200
