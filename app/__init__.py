from flask import Flask
from flask_admin import Admin
from app import api, view
from app.config import config
from app.extensions import config_extensions
from app.models import init_admin


def create_app(config_name):
    app = Flask(__name__)
    
    # 加载配置项
    app.config.from_object(config.get(config_name))

    # 初始化管理视图
    init_admin(app)
    # 加载拓展
    config_extensions(app)
    # 加载蓝图
    api.config_blueprint(app)
    view.config_blueprint(app)

    return app