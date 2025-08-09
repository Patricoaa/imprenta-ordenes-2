import os
from flask import Flask
from dotenv import load_dotenv
from flask_wtf.csrf import generate_csrf

load_dotenv()

from .config import get_config
from .extensions import db, migrate, login_manager, csrf


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False, template_folder="templates", static_folder="static")

    # Config
    cfg = get_config(config_name)
    app.config.from_object(cfg)

    # Ensure folders
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Login settings
    from .models import Usuario

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(Usuario, int(user_id))

    login_manager.login_view = "usuarios.login"

    # Register blueprints
    register_blueprints(app)

    # Register CLI commands
    register_cli(app)

    # Template context processors
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    # CSRF exemptions where necessary (example: webhook endpoints could be exempted)
    # from .modules.api.routes import api_bp
    # csrf.exempt(api_bp)

    return app


def register_blueprints(app: Flask) -> None:
    from .modules.clientes.routes import bp as clientes_bp
    from .modules.vendedores.routes import bp as vendedores_bp
    from .modules.ordenes.routes import bp as ordenes_bp
    from .modules.pagos.routes import bp as pagos_bp
    from .modules.usuarios.routes import bp as usuarios_bp
    from .modules.configuraciones.routes import bp as configuraciones_bp
    from .modules.dashboard.routes import bp as dashboard_bp
    from .modules.calendario.routes import bp as calendario_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(vendedores_bp)
    app.register_blueprint(ordenes_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(configuraciones_bp)
    app.register_blueprint(calendario_bp)


def register_cli(app: Flask) -> None:
    @app.cli.command("ensure-admin")
    def ensure_admin():
        """Create an admin user if no users exist."""
        from .models import Usuario
        from werkzeug.security import generate_password_hash
        with app.app_context():
            if db.session.query(Usuario).count() == 0:
                admin_name = os.getenv("ADMIN_NAME", "Admin")
                admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
                admin_password = os.getenv("ADMIN_PASSWORD", "admin1234")
                user = Usuario(
                    nombre=admin_name,
                    email=admin_email,
                    rol="admin",
                    password_hash=generate_password_hash(admin_password)
                )
                db.session.add(user)
                db.session.commit()
                print(f"Created admin user: {admin_email}")
            else:
                print("Admin user creation skipped; users already exist.")