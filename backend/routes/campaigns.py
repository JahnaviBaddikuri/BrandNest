# campaigns routes

from flask import Blueprint, request, jsonify
from models import db, Campaign, Brand
from datetime import datetime

campaigns_bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


@campaigns_bp.route('', methods=['GET'])
def get_campaigns():
    # list campaigns
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', type=str)
        brand_id = request.args.get('brand_id', type=int)

        query = Campaign.query
        if status:
            query = query.filter_by(status=status)
        if brand_id:
            query = query.filter_by(brand_id=brand_id)

        campaigns = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'status': 'success',
            'data': [campaign.to_dict() for campaign in campaigns.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': campaigns.total,
                'pages': campaigns.pages
            }
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': 'error'}), 500


@campaigns_bp.route('/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    # get campaign
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        return jsonify({'status': 'success', 'data': campaign.to_dict()}), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': 'error'}), 500


@campaigns_bp.route('', methods=['POST'])
def create_campaign():
    # create campaign
    try:
        data = request.get_json()

        required = ['brand_id', 'title', 'description', 'budget', 'target_platform', 'start_date', 'end_date']
        missing = [f for f in required if not data.get(f)]

        if missing:
            return jsonify({'status': 'error', 'message': f'missing: {", ".join(missing)}'}), 400

        brand = Brand.query.get(data['brand_id'])
        if not brand:
            return jsonify({'status': 'error', 'message': 'brand not found'}), 404

        campaign = Campaign(
            brand_id=data['brand_id'],
            title=data['title'],
            description=data['description'],
            budget=data['budget'],
            target_platform=data['target_platform'],
            target_category=data.get('target_category'),
            min_followers=data.get('min_followers', 0),
            max_budget_per_creator=data.get('max_budget_per_creator'),
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
        )

        db.session.add(campaign)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'created',
            'data': campaign.to_dict()
        }), 201

    except ValueError as error:
        return jsonify({'status': 'error', 'message': 'bad date'}), 400
    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500


@campaigns_bp.route('/<int:campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    # update campaign
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        data = request.get_json()
        updatable = ['title', 'description', 'budget', 'target_platform', 'target_category', 'min_followers', 'max_budget_per_creator', 'status']

        for field in updatable:
            if field in data:
                setattr(campaign, field, data[field])

        campaign.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'updated',
            'data': campaign.to_dict()
        }), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500


@campaigns_bp.route('/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    # delete campaign
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        db.session.delete(campaign)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'deleted'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500
