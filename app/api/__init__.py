from app.api.maps import maps

DEFAULT_BLUEPRINT = [
    (maps, '/api/maps/'),
]

def config_blueprint(app):
    for blueprint, prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blueprint, url_prefix=prefix)
