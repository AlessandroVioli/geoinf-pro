from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def config_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)