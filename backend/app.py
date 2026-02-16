from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import get_config
from models import db
from routes import register_routes
from email_service import init_mail
import os


def create_app():
    config = get_config()
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.init_app(app)
    init_mail(app)  # Initialize email service
    CORS(app)
    register_routes(app)
    
    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'status': 'error', 'message': 'not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'status': 'error', 'message': 'server error'}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok'}), 200

    @app.route('/uploads/<path:filename>', methods=['GET'])
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app



app = create_app()


if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=5000)
