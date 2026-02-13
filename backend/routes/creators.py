from flask import Blueprint, request, jsonify, current_app
from models import db, Creator
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

creators_bp = Blueprint('creators', __name__, url_prefix='/api/creators')

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def is_allowed_image(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_IMAGE_EXTENSIONS


@creators_bp.route('/upload-profile', methods=['POST'])
def upload_profile_image():
    print('🔍 Upload request received')
    print('   request.files:', request.files)
    print('   request.form:', request.form)
    print('   request.content_type:', request.content_type)
    
    if 'file' not in request.files:
        print('❌ No file found in request.files')
        return jsonify({'status': 'error', 'message': 'missing file'}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'status': 'error', 'message': 'empty file'}), 400

    if not is_allowed_image(file.filename):
        return jsonify({'status': 'error', 'message': 'invalid file type'}), 400

    safe_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    upload_root = current_app.config['UPLOAD_FOLDER']
    creator_dir = os.path.join(upload_root, 'creators')
    os.makedirs(creator_dir, exist_ok=True)
    file_path = os.path.join(creator_dir, unique_name)
    file.save(file_path)

    public_url = f"{request.host_url.rstrip('/')}/uploads/creators/{unique_name}"
    return jsonify({'status': 'success', 'data': {'url': public_url}}), 201


@creators_bp.route('', methods=['GET'])
def get_creators():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        platform = request.args.get('platform', type=str)
        category = request.args.get('category', type=str)

        query = Creator.query
        if platform:
            query = query.filter_by(platform=platform)
        if category:
            query = query.filter_by(category=category)

        creators = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'status': 'success',
            'data': [creator.to_dict() for creator in creators.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': creators.total,
                'pages': creators.pages
            }
        }), 200

    except Exception as error:
        return jsonify({
            'status': 'error',
            'message': 'error'
        }), 500


@creators_bp.route('/<int:creator_id>', methods=['GET'])
def get_creator(creator_id):
    try:
        creator = Creator.query.get(creator_id)
        if not creator:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        return jsonify({'status': 'success', 'data': creator.to_dict()}), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': 'error'}), 500


@creators_bp.route('', methods=['POST'])
def create_creator():
    
    try:
        data = request.get_json()

        required = ['firebase_uid', 'username', 'email', 'platform', 'category', 'rate']
        missing = [f for f in required if not data.get(f)]

        if missing:
            return jsonify({
                'status': 'error',
                'message': f'missing: {", ".join(missing)}'
            }), 400

        # Check if Firebase UID already exists
        if Creator.query.filter_by(firebase_uid=data['firebase_uid']).first():
            return jsonify({'status': 'error', 'message': 'account already exists'}), 400

        if Creator.query.filter_by(username=data['username']).first():
            return jsonify({'status': 'error', 'message': 'username exists'}), 400

        if Creator.query.filter_by(email=data['email']).first():
            return jsonify({'status': 'error', 'message': 'email exists'}), 400

        creator = Creator(
            firebase_uid=data['firebase_uid'],
            username=data['username'],
            email=data['email'],
            platform=data['platform'],
            followers_count=data.get('followers_count', 0),
            engagement_rate=data.get('engagement_rate', 0.0),
            category=data['category'],
            location=data.get('location'),
            rate=data['rate'],
            bio=data.get('bio'),
            profile_image_url=data.get('profile_image_url'),
        )

        db.session.add(creator)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'created',
            'data': creator.to_dict()
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500


@creators_bp.route('/<int:creator_id>', methods=['PUT'])
def update_creator(creator_id):
    
    try:
        creator = Creator.query.get(creator_id)
        if not creator:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        data = request.get_json()
        updatable = [
            'followers_count', 'engagement_rate', 'location',
            'rate', 'bio', 'profile_image_url', 'is_verified'
        ]

        for field in updatable:
            if field in data:
                setattr(creator, field, data[field])

        creator.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'updated',
            'data': creator.to_dict()
        }), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500


@creators_bp.route('/<int:creator_id>', methods=['DELETE'])
def delete_creator(creator_id):
    
    try:
        creator = Creator.query.get(creator_id)
        if not creator:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        db.session.delete(creator)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'deleted'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500
