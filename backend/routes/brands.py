# brands routes

from flask import Blueprint, request, jsonify, current_app
from models import db, Brand, ContactRequest, Campaign, Application, Order, Message, Notification, Review
from datetime import datetime
from werkzeug.utils import secure_filename
from jwt_auth import require_auth
import os
import uuid

brands_bp = Blueprint('brands', __name__, url_prefix='/api/brands')

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def is_allowed_image(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_IMAGE_EXTENSIONS


@brands_bp.route('/upload-logo', methods=['POST'])
def upload_brand_logo():
    print('📤 Brand logo upload request received')
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
    brand_dir = os.path.join(upload_root, 'brands')
    os.makedirs(brand_dir, exist_ok=True)
    file_path = os.path.join(brand_dir, unique_name)
    file.save(file_path)

    public_url = f"{request.host_url.rstrip('/')}/uploads/brands/{unique_name}"
    return jsonify({'status': 'success', 'data': {'url': public_url}}), 201


@brands_bp.route('', methods=['GET'], strict_slashes=False)
def get_brands():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        industry = request.args.get('industry', type=str)

        query = Brand.query
        if industry:
            query = query.filter_by(industry=industry)

        brands = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'status': 'success',
            'data': [brand.to_dict() for brand in brands.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': brands.total,
                'pages': brands.pages
            }
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': 'error'}), 500


@brands_bp.route('/<int:brand_id>', methods=['GET'])
def get_brand(brand_id):

    try:
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        return jsonify({'status': 'success', 'data': brand.to_dict()}), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': 'error'}), 500


@brands_bp.route('', methods=['POST'], strict_slashes=False)
def create_brand():
    """
    DEPRECATED: Use /api/auth/register/brand instead
    
    This endpoint is kept for backward compatibility but should not be used.
    Registration is now handled through the auth routes which includes
    password management and JWT token generation.
    """
    return jsonify({
        'status': 'error',
        'message': 'This endpoint is deprecated. Please use /api/auth/register/brand for registration'
    }), 410  # 410 Gone status code


@brands_bp.route('/<int:brand_id>', methods=['PUT'])
def update_brand(brand_id):
    
    try:
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        data = request.get_json()
        updatable = ['location', 'website', 'logo_url', 'verified']

        for field in updatable:
            if field in data:
                setattr(brand, field, data[field])

        brand.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'updated',
            'data': brand.to_dict()
        }), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500


@brands_bp.route('/<int:brand_id>', methods=['DELETE'])
@require_auth
def delete_brand(brand_id, **kwargs):
    current_user = kwargs.get('current_user', {})
    if current_user.get('role') != 'brand' or current_user.get('user_id') != brand_id:
        return jsonify({'status': 'error', 'message': 'unauthorized'}), 403

    try:
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        # Get all campaign IDs owned by this brand
        campaign_ids = [c.id for c in Campaign.query.filter_by(brand_id=brand_id).all()]

        # Delete reviews linked to orders placed by this brand
        brand_orders = Order.query.filter_by(brand_id=brand_id).all()
        brand_order_ids = [o.id for o in brand_orders]
        if brand_order_ids:
            Review.query.filter(Review.order_id.in_(brand_order_ids)).delete(synchronize_session=False)

        # Delete orders placed by this brand
        Order.query.filter_by(brand_id=brand_id).delete(synchronize_session=False)

        # Delete applications for campaigns owned by this brand
        if campaign_ids:
            Application.query.filter(Application.campaign_id.in_(campaign_ids)).delete(synchronize_session=False)

        # Delete campaigns owned by this brand
        Campaign.query.filter_by(brand_id=brand_id).delete(synchronize_session=False)

        # Delete contact requests involving this brand
        ContactRequest.query.filter_by(brand_id=brand_id).delete(synchronize_session=False)

        # Delete messages sent or received by this brand
        Message.query.filter(
            ((Message.sender_role == 'brand') & (Message.sender_id == brand_id)) |
            ((Message.receiver_role == 'brand') & (Message.receiver_id == brand_id))
        ).delete(synchronize_session=False)

        # Delete notifications for this brand
        Notification.query.filter_by(user_role='brand', user_id=brand_id).delete(synchronize_session=False)

        # Finally delete the brand
        db.session.delete(brand)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Account deleted successfully'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500
