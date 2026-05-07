import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///weight_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SMTP_HOST = 'smtp.qq.com'
    SMTP_PORT = 587
    SMTP_USER = '1329791448@qq.com'
    SMTP_PASS = 'fpmcilnasevkgebb'

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
