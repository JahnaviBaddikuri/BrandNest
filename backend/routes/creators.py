from flask import Blueprint, request, jsonify, current_app
from models import db, Creator, ContactRequest, Application, Order, Message, Notification, Review
from datetime import datetime
from werkzeug.utils import secure_filename
from jwt_auth import require_auth
import os
import uuid

creators_bp = Blueprint('creators', __name__, url_prefix='/api/creators')

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def is_allowed_image(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_IMAGE_EXTENSIONS


@creators_bp.route('/upload-profile', methods=['POST'])
def upload_profile_image():
    print('   Upload request received')
    print('   request.files:', request.files)
    print('   request.form:', request.form)
    print('   request.content_type:', request.content_type)
    
    if 'file' not in request.files:
        print('  No file found in request.files')
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
    """
    DEPRECATED: Use /api/auth/register/creator instead
    
    This endpoint is kept for backward compatibility but should not be used.
    Registration is now handled through the auth routes which includes
    password management and JWT token generation.
    """
    return jsonify({
        'status': 'error',
        'message': 'This endpoint is deprecated. Please use /api/auth/register/creator for registration'
    }), 410  # 410 Gone status code


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
@require_auth
def delete_creator(creator_id, **kwargs):
    """
    DELETE endpoint - authenticated users deleting their own account
    """
    current_user = kwargs.get('current_user', {})
    if current_user.get('role') != 'creator' or current_user.get('user_id') != creator_id:
        return jsonify({'status': 'error', 'message': 'unauthorized'}), 403

    try:
        creator = Creator.query.get(creator_id)
        if not creator:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        # Delete reviews linked to orders received by this creator
        creator_orders = Order.query.filter_by(creator_id=creator_id).all()
        creator_order_ids = [o.id for o in creator_orders]
        if creator_order_ids:
            Review.query.filter(Review.order_id.in_(creator_order_ids)).delete(synchronize_session=False)

        # Delete orders received by this creator
        Order.query.filter_by(creator_id=creator_id).delete(synchronize_session=False)

        # Delete applications submitted by this creator
        Application.query.filter_by(creator_id=creator_id).delete(synchronize_session=False)

        # Delete contact requests involving this creator
        ContactRequest.query.filter_by(creator_id=creator_id).delete(synchronize_session=False)

        # Delete messages sent or received by this creator
        Message.query.filter(
            ((Message.sender_role == 'creator') & (Message.sender_id == creator_id)) |
            ((Message.receiver_role == 'creator') & (Message.receiver_id == creator_id))
        ).delete(synchronize_session=False)

        # Delete notifications for this creator
        Notification.query.filter_by(user_role='creator', user_id=creator_id).delete(synchronize_session=False)

        # Finally delete the creator
        db.session.delete(creator)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Account deleted successfully'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500
