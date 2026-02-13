"""
Admin Routes
Handles admin operations: viewing pending users and approving accounts
"""

from flask import Blueprint, request, jsonify
from models import db, Creator, Brand
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/pending-users', methods=['GET'])
def get_pending_users():
    """
    Get all pending users (creators and brands) awaiting verification
    Returns creators with is_verified=False and brands with verified=False
    """
    try:
        # Fetch unverified creators
        pending_creators = Creator.query.filter_by(is_verified=False).all()
        
        # Fetch unverified brands
        pending_brands = Brand.query.filter_by(verified=False).all()
        
        # Convert to dictionaries
        creators_data = [creator.to_dict() for creator in pending_creators]
        brands_data = [brand.to_dict() for brand in pending_brands]
        
        return jsonify({
            'status': 'success',
            'data': {
                'creators': creators_data,
                'brands': brands_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch pending users: {str(e)}'
        }), 500


@admin_bp.route('/approve/creator/<int:creator_id>', methods=['POST'])
def approve_creator(creator_id):
    """
    Approve a creator account by setting is_verified to True
    """
    try:
        creator = Creator.query.get(creator_id)
        
        if not creator:
            return jsonify({
                'status': 'error',
                'message': 'Creator not found'
            }), 404
        
        if creator.is_verified:
            return jsonify({
                'status': 'error',
                'message': 'Creator is already verified'
            }), 400
        
        # Update verification status
        creator.is_verified = True
        creator.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Creator approved successfully',
            'data': creator.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to approve creator: {str(e)}'
        }), 500


@admin_bp.route('/approve/brand/<int:brand_id>', methods=['POST'])
def approve_brand(brand_id):
    """
    Approve a brand account by setting verified to True
    """
    try:
        brand = Brand.query.get(brand_id)
        
        if not brand:
            return jsonify({
                'status': 'error',
                'message': 'Brand not found'
            }), 404
        
        if brand.verified:
            return jsonify({
                'status': 'error',
                'message': 'Brand is already verified'
            }), 400
        
        # Update verification status
        brand.verified = True
        brand.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Brand approved successfully',
            'data': brand.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to approve brand: {str(e)}'
        }), 500


@admin_bp.route('/stats', methods=['GET'])
def get_admin_stats():
    """
    Get admin statistics: total users, pending approvals, verified users
    """
    try:
        total_creators = Creator.query.count()
        verified_creators = Creator.query.filter_by(is_verified=True).count()
        pending_creators = Creator.query.filter_by(is_verified=False).count()
        
        total_brands = Brand.query.count()
        verified_brands = Brand.query.filter_by(verified=True).count()
        pending_brands = Brand.query.filter_by(verified=False).count()
        
        return jsonify({
            'status': 'success',
            'data': {
                'creators': {
                    'total': total_creators,
                    'verified': verified_creators,
                    'pending': pending_creators
                },
                'brands': {
                    'total': total_brands,
                    'verified': verified_brands,
                    'pending': pending_brands
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch stats: {str(e)}'
        }), 500
