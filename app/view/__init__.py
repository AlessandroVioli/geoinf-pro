from app.view.maps import maps
from app.view.workflow import workflows

DEFAULT_BLUEPRINT = [
    (maps, '/maps/'),
    (workflows, '/workflow/'),
]

def config_blueprint(app):
    for blueprint, prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blueprint, url_prefix=prefix)
