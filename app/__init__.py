# -*— coding:utf-8 -*—
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_message = '请先登录'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    # 工厂方式创建 flask 实例
    app = Flask(__name__)

    # 从配置类中加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化用到的各个模块（关联到当前app）
    db.init_app(app)
    db.app = app
    login_manager.init_app(app)

    # 注册蓝图(导入包初始化模块__init__中的内容时，需要加‘.’)
    from .main import main as main_bp
    from .auth import auth as auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,url_prefix='/admin')

    # 返回 flask 实例
    return app






