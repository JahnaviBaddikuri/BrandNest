# campaigns routes

from flask import Blueprint, request, jsonify
from models import db, Campaign, Brand
from jwt_auth import require_auth
from datetime import datetime

campaigns_bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


@campaigns_bp.route('', methods=['GET'])
def get_campaigns():
    # list campaigns (public)
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', type=str)
        brand_id = request.args.get('brand_id', type=int)
        platform = request.args.get('platform', type=str)
        category = request.args.get('category', type=str)

        query = Campaign.query
        if status:
            query = query.filter_by(status=status)
        else:
            query = query.filter_by(status='active')
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        if platform:
            query = query.filter_by(target_platform=platform)
        if category:
            query = query.filter_by(target_category=category)

        campaigns = query.order_by(Campaign.created_at.desc()).paginate(page=page, per_page=per_page)

        return jsonify({
            'status': 'success',
            'data': [campaign.to_dict(include_brand=True) for campaign in campaigns.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': campaigns.total,
                'pages': campaigns.pages
            }
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@campaigns_bp.route('/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        return jsonify({'status': 'success', 'data': campaign.to_dict(include_brand=True)}), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@campaigns_bp.route('', methods=['POST'])
@require_auth
def create_campaign(current_user):
    # create campaign (brand only)
    try:
        if current_user.get('role') != 'brand':
            return jsonify({'status': 'error', 'message': 'Only brands can create campaigns'}), 403

        data = request.get_json()
        brand_id = current_user.get('user_id')

        required = ['title', 'description']
        missing = [f for f in required if not data.get(f)]

        if missing:
            return jsonify({'status': 'error', 'message': f'missing: {", ".join(missing)}'}), 400

        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({'status': 'error', 'message': 'brand not found'}), 404

        campaign = Campaign(
            brand_id=brand_id,
            title=data['title'],
            description=data['description'],
            budget=data.get('budget'),
            target_platform=data.get('target_platform'),
            target_category=data.get('target_category'),
            min_followers=data.get('min_followers', 0),
            max_budget_per_creator=data.get('max_budget_per_creator'),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
        )

        db.session.add(campaign)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Campaign created',
            'data': campaign.to_dict(include_brand=True)
        }), 201

    except ValueError as error:
        return jsonify({'status': 'error', 'message': 'Invalid date format'}), 400
    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500


@campaigns_bp.route('/my', methods=['GET'])
@require_auth
def get_my_campaigns(current_user):
    """Get campaigns for the authenticated brand"""
    try:
        if current_user.get('role') != 'brand':
            return jsonify({'status': 'error', 'message': 'Only brands can view their campaigns'}), 403

        brand_id = current_user.get('user_id')
        status = request.args.get('status', type=str)

        query = Campaign.query.filter_by(brand_id=brand_id)
        if status:
            query = query.filter_by(status=status)
        
        campaigns = query.order_by(Campaign.created_at.desc()).all()

        return jsonify({
            'status': 'success',
            'data': [c.to_dict(include_brand=True) for c in campaigns]
        }), 200
    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@campaigns_bp.route('/<int:campaign_id>', methods=['PUT'])
@require_auth
def update_campaign(campaign_id, current_user):
    try:
        if current_user.get('role') != 'brand':
            return jsonify({'status': 'error', 'message': 'Only brands can update campaigns'}), 403

        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        if campaign.brand_id != current_user.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        data = request.get_json()
        updatable = ['title', 'description', 'budget', 'target_platform', 'target_category', 'min_followers', 'max_budget_per_creator', 'status']

        for field in updatable:
            if field in data:
                setattr(campaign, field, data[field])

        if 'start_date' in data:
            campaign.start_date = datetime.fromisoformat(data['start_date'])
        if 'end_date' in data:
            campaign.end_date = datetime.fromisoformat(data['end_date'])

        campaign.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'updated',
            'data': campaign.to_dict(include_brand=True)
        }), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500


@campaigns_bp.route('/<int:campaign_id>', methods=['DELETE'])
@require_auth
def delete_campaign(campaign_id, current_user):
    try:
        if current_user.get('role') != 'brand':
            return jsonify({'status': 'error', 'message': 'Only brands can delete campaigns'}), 403

        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        if campaign.brand_id != current_user.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        db.session.delete(campaign)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'deleted'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500
