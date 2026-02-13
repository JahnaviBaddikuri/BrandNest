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
    
    try:
        data = request.get_json()

        required = ['firebase_uid', 'company_name', 'email', 'industry']
        missing = [f for f in required if not data.get(f)]

        if missing:
            return jsonify({
                'status': 'error',
                'message': f'missing: {", ".join(missing)}'
            }), 400

        # Check if Firebase UID already exists
        if Brand.query.filter_by(firebase_uid=data['firebase_uid']).first():
            return jsonify({'status': 'error', 'message': 'account already exists'}), 400

        if Brand.query.filter_by(company_name=data['company_name']).first():
            return jsonify({'status': 'error', 'message': 'name exists'}), 400

        if Brand.query.filter_by(email=data['email']).first():
            return jsonify({'status': 'error', 'message': 'email exists'}), 400

        brand = Brand(
            firebase_uid=data['firebase_uid'],
            company_name=data['company_name'],
            email=data['email'],
            industry=data['industry'],
            location=data.get('location'),
            website=data.get('website'),
            logo_url=data.get('logo_url'),
        )

        db.session.add(brand)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'created',
            'data': brand.to_dict()
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500


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
