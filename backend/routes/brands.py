# brands routes

from flask import Blueprint, request, jsonify
from models import db, Brand
from datetime import datetime

brands_bp = Blueprint('brands', __name__, url_prefix='/api/brands')


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
def delete_brand(brand_id):
    # delete brand
    try:
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        db.session.delete(brand)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'deleted'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500
