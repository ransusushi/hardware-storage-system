"""Flask application factory for the Hardware Storage System."""
from __future__ import annotations

from flask import Flask

from .config import Config


def create_app(config: Config | None = None) -> Flask:
    """Application factory."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config or Config())

    # Database lifecycle
    from . import db as _db

    @app.before_request
    def _load_user() -> None:
        from . import auth as _auth

        _auth.load_current_user()

    app.teardown_appcontext(_db.close_connection)

    # Blueprints
    from .auth import bp as auth_bp
    from .views.dashboard import bp as dashboard_bp
    from .views.products import bp as products_bp
    from .views.categories import bp as categories_bp
    from .views.suppliers import bp as suppliers_bp
    from .views.warehouses import bp as warehouses_bp
    from .views.stock import bp as stock_bp
    from .views.customers import bp as customers_bp
    from .views.orders import bp as orders_bp
    from .views.employees import bp as employees_bp
    from .views.queries import bp as queries_bp
    from .views.reports import bp as reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(warehouses_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(queries_bp)
    app.register_blueprint(reports_bp)

    @app.context_processor
    def _inject_globals():
        from flask import g

        return {"current_user": getattr(g, "user", None)}

    return app
