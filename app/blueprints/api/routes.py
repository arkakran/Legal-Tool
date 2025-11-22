import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from loguru import logger

from app.utils.validators import validate_pdf, validate_file_size
from app.services.pipeline import AnalysisPipeline

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    settings = current_app.config['SETTINGS']

    # Validate PDF
    is_valid, error_msg = validate_pdf(file)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    # Validate file size
    is_valid, error_msg = validate_file_size(file, settings.MAX_CONTENT_LENGTH)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    # Secure filename
    original_filename = secure_filename(file.filename)

    # Save file temporarily
    import time
    timestamp = int(time.time() * 1000)
    temp_filename = f"{timestamp}_{original_filename}"
    filepath = os.path.join(settings.UPLOAD_FOLDER, temp_filename)

    try:
        # Save uploaded file
        file.save(filepath)
        logger.info(f"File saved: {temp_filename}")

        # Initialize pipeline
        pipeline = AnalysisPipeline(settings)

        # Run analysis
        logger.info(f"Starting analysis for: {original_filename}")
        result = pipeline.analyze_document(filepath, original_filename)

        # Clean up uploaded file
        try:
            os.remove(filepath)
            logger.info(f"Cleaned up temp file: {temp_filename}")
        except Exception as e:
            logger.warning(f"Failed to delete temp file: {e}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Analysis failed: {e}")

        # Clean up on error
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

        return jsonify({'error': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200
