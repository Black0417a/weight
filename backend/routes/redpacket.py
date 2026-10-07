from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import WeightRecord, RedPacketRecord, User, get_beijing_time
from datetime import timedelta
from sqlalchemy import or_, and_
import random

redpacket_bp = Blueprint('redpacket', __name__)

STREAK_REQUIRED = 7
MIN_AMOUNT = 0.01
MAX_AMOUNT = 100.0


def get_streak_info(user_id):
    """计算当前连续打卡天数（打卡=记录体重）。

    红包每个周期只能抽取一次：抽取后从抽取当天重新计数，
    仅统计抽取日之后的新打卡，需再连续打卡7天才能再次抽取。
    返回 (连续天数, 本次连续打卡起始日, 最近打卡日)
    """
    last_draw = RedPacketRecord.query.filter_by(user_id=user_id) \
        .order_by(RedPacketRecord.created_at.desc()).first()

    query = WeightRecord.query.filter(WeightRecord.user_id == user_id)
    if last_draw and last_draw.created_at:
        # 以抽取时刻为界：抽取日之前的打卡全部作废；抽取当天在抽取之后
        # 新记录的体重计入新周期，避免"抽取后记录体重计数不变"的问题
        draw_date = last_draw.created_at.date()
        query = query.filter(
            or_(
                WeightRecord.record_date > draw_date,
                and_(
                    WeightRecord.record_date == draw_date,
                    WeightRecord.created_at > last_draw.created_at
                )
            )
        )

    records = query.order_by(WeightRecord.record_date.desc()).all()
    if not records:
        return 0, None, None

    dates = {r.record_date for r in records}
    latest_date = records[0].record_date
    streak_start = latest_date
    d = latest_date
    while d in dates:
        streak_start = d
        d = d - timedelta(days=1)

    streak = (latest_date - streak_start).days + 1
    return streak, streak_start, latest_date


@redpacket_bp.route('/redpacket/status', methods=['GET'])
@jwt_required()
def redpacket_status():
    """首页红包打卡状态：连续打卡天数、还差X天可领取"""
    user_id = int(get_jwt_identity())
    streak, _, _ = get_streak_info(user_id)
    total_drawn = RedPacketRecord.query.filter_by(user_id=user_id).count()

    return jsonify({
        'streak': streak,
        'streak_required': STREAK_REQUIRED,
        'remaining_days': max(0, STREAK_REQUIRED - streak),
        'can_draw': streak >= STREAK_REQUIRED,
        'total_drawn': total_drawn
    }), 200


@redpacket_bp.route('/redpacket/draw', methods=['POST'])
@jwt_required()
def draw_redpacket():
    """连续打卡7天后抽取随机红包，金额0.01~100元"""
    user_id = int(get_jwt_identity())
    streak, streak_start, _ = get_streak_info(user_id)

    if streak_start is None or streak < STREAK_REQUIRED:
        return jsonify({'error': f'需连续打卡{STREAK_REQUIRED}天才能抽取，当前连续{streak}天'}), 400

    # 防重复抽取：该打卡窗口已有红包记录
    window_end = streak_start + timedelta(days=STREAK_REQUIRED - 1)
    exists = RedPacketRecord.query.filter_by(
        user_id=user_id, streak_start=streak_start
    ).first()
    if exists:
        return jsonify({'error': '该周期红包已抽取过，需重新连续打卡7天才可再抽取'}), 400

    amount = round(random.uniform(MIN_AMOUNT, MAX_AMOUNT), 2)
    packet = RedPacketRecord(
        user_id=user_id,
        amount=amount,
        streak_start=streak_start,
        streak_end=window_end
    )
    db.session.add(packet)
    db.session.commit()

    user = User.query.get(user_id)
    return jsonify({
        'id': packet.id,
        'amount': amount,
        'email': user.email if user else None,
        'streak_start': packet.streak_start.isoformat(),
        'streak_end': packet.streak_end.isoformat(),
        'created_at': get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')
    }), 200


@redpacket_bp.route('/redpacket/history', methods=['GET'])
@jwt_required()
def redpacket_history():
    """用户已抽取的红包记录（用于查看/截图兑换）"""
    user_id = int(get_jwt_identity())
    packets = RedPacketRecord.query.filter_by(user_id=user_id) \
        .order_by(RedPacketRecord.created_at.desc()).all()

    user = User.query.get(user_id)
    email = user.email if user else None
    result = []
    for p in packets:
        item = p.to_dict()
        item['email'] = email
        item['drawn_at'] = p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else None
        result.append(item)
    return jsonify(result), 200
