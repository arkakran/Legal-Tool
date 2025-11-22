from app import create_app
from loguru import logger

app = create_app()

if __name__ == '__main__':
    logger.info("Starting Flask development server...")
    app.run(host='127.0.0.1', port=5000, debug=True)  # Localhost only for safe development
