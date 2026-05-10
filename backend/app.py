from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
import os

db = SQLAlchemy()
jwt = JWTManager()
scheduler = BackgroundScheduler()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    jwt.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from routes.auth import auth_bp
    from routes.weights import weights_bp
    from routes.goal import goal_bp
    from routes.admin import admin_bp
    from routes.reminder import reminder_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(weights_bp, url_prefix='/api')
    app.register_blueprint(goal_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(reminder_bp, url_prefix='/api')

    with app.app_context():
        from models import User, WeightRecord, UserGoal, Admin, RewardRule, UserReward, SystemConfig, UserReminderSetting
        db.create_all()

        if not SystemConfig.query.first():
            defaults = [
                SystemConfig(key='page_size', value='20', description='默认分页大小'),
                SystemConfig(key='token_expire_hours', value='24', description='Token过期时间(小时)'),
            ]
            db.session.add_all(defaults)
            db.session.commit()

        from utils.email import check_and_send_reminders
        if not scheduler.running:
            scheduler.add_job(
                func=lambda: check_and_send_reminders(app),
                trigger=CronTrigger(hour=20, minute=0, timezone='Asia/Shanghai'),
                id='weight_reminder'
            )
            scheduler.start()

    return app
