# route registration

from .creators import creators_bp
from .brands import brands_bp
from .auth import auth_bp
from .admin import admin_bp
from .contact_requests import contact_requests_bp
from .campaigns import campaigns_bp
from .applications import applications_bp
from .messages import messages_bp
from .notifications import notifications_bp
from .orders import orders_bp
from .reviews import reviews_bp


def register_routes(app):
    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(creators_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(contact_requests_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
