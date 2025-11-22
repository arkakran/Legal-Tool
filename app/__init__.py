from flask import Flask
from loguru import logger

from app.config import get_config
from app.extensions import init_extensions


def create_app() -> Flask:
    # Load configuration with fail-fast validation
    try:
        settings = get_config()
        logger.info(f"Configuration loaded: {settings.FLASK_ENV} environment")
    except Exception as e:
        logger.error(f"Configuration failed: {e}")
        raise

    # Create Flask app
    app = Flask(__name__)

    # Configure Flask from settings
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
    app.config['SETTINGS'] = settings

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    logger.info("Flask app created successfully")

    return app
