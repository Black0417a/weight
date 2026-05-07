from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
import os

db = SQLAlchemy()
jwt = JWTManager()
scheduler = BackgroundScheduler()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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
        from models import User, WeightRecord, UserGoal, Admin, RewardRule, SystemConfig, UserReminderSetting
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
                trigger='cron',
                hour=20,
                minute=0,
                id='weight_reminder'
            )
            scheduler.start()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=6000)
