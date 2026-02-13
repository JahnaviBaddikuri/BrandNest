# route registration

from .creators import creators_bp
from .brands import brands_bp
from .campaigns import campaigns_bp
from .applications import applications_bp
from .auth import auth_bp


def register_routes(app):
    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(creators_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(applications_bp)
