from app import db
from datetime import datetime, timedelta, timezone
import json

def get_beijing_time():
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8), 'Asia/Shanghai')
    return utc_now.astimezone(beijing_tz)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    height = db.Column(db.Float, nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=get_beijing_time)
    updated_at = db.Column(db.DateTime, default=get_beijing_time, onupdate=get_beijing_time)

    weight_records = db.relationship('WeightRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    goal = db.relationship('UserGoal', backref='user', uselist=False, cascade='all, delete-orphan')
    reminder_setting = db.relationship('UserReminderSetting', backref='user', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        reminder_setting = self.reminder_setting
        return {
            'id': self.id,
            'email': self.email,
            'height': self.height,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'record_count': self.weight_records.count(),
            'email_reminder_enabled': reminder_setting.email_reminder_enabled if reminder_setting else True
        }


class WeightRecord(db.Model):
    __tablename__ = 'weight_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    __table_args__ = (db.UniqueConstraint('user_id', 'record_date', name='uq_user_date'),)

    def to_dict(self):
        return {
            'id': self.id,
            'weight': self.weight,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserGoal(db.Model):
    __tablename__ = 'user_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    target_weight = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_beijing_time, onupdate=get_beijing_time)

    def to_dict(self):
        return {
            'id': self.id,
            'target_weight': self.target_weight,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RewardRule(db.Model):
    __tablename__ = 'reward_rules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    condition_type = db.Column(db.String(50), nullable=False)
    condition_params = db.Column(db.Text, nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)
    reward_content = db.Column(db.Text, nullable=True)
    reward_image = db.Column(db.String(500), nullable=True)
    grant_mode = db.Column(db.String(50), nullable=False)
    target_users = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'condition_type': self.condition_type,
            'condition_params': json.loads(self.condition_params) if self.condition_params else {},
            'reward_type': self.reward_type,
            'reward_content': self.reward_content,
            'reward_image': self.reward_image,
            'grant_mode': self.grant_mode,
            'target_users': json.loads(self.target_users) if self.target_users else 'all',
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserReminderSetting(db.Model):
    __tablename__ = 'user_reminder_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    email_reminder_enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=get_beijing_time, onupdate=get_beijing_time)

    def to_dict(self):
        return {
            'id': self.id,
            'email_reminder_enabled': self.email_reminder_enabled,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UserReward(db.Model):
    __tablename__ = 'user_rewards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('reward_rules.id'), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)
    reward_content = db.Column(db.Text, nullable=True)
    reward_image = db.Column(db.String(500), nullable=True)
    weight_value = db.Column(db.Float, nullable=True)
    target_weight = db.Column(db.Float, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    rule = db.relationship('RewardRule', backref='user_rewards')

    def to_dict(self):
        rule_name = None
        condition_type = None
        try:
            if self.rule:
                rule_name = self.rule.name
                condition_type = self.rule.condition_type
        except Exception:
            rule_name = None
            condition_type = None
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'rule_name': rule_name,
            'condition_type': condition_type,
            'reward_type': self.reward_type,
            'reward_content': self.reward_content,
            'reward_image': self.reward_image,
            'weight_value': self.weight_value,
            'target_weight': self.target_weight,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SystemConfig(db.Model):
    __tablename__ = 'system_configs'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description
        }
