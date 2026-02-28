# applications routes

from flask import Blueprint, request, jsonify
from models import db, Application, Campaign, Creator, Brand, ContactRequest
from jwt_auth import require_auth
from datetime import datetime

applications_bp = Blueprint('applications', __name__, url_prefix='/api/applications')


@applications_bp.route('', methods=['GET'])
@require_auth
def get_applications(current_user):
    """List applications - creators see their own, brands see apps for their campaigns"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', type=str)
        campaign_id = request.args.get('campaign_id', type=int)
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        query = Application.query

        if role == 'creator':
            query = query.filter_by(creator_id=user_id)
        elif role == 'brand':
            # Brands see applications for their campaigns
            brand_campaigns = Campaign.query.filter_by(brand_id=user_id).with_entities(Campaign.id).all()
            campaign_ids = [c.id for c in brand_campaigns]
            query = query.filter(Application.campaign_id.in_(campaign_ids))

        if status:
            query = query.filter_by(status=status)
        if campaign_id:
            query = query.filter_by(campaign_id=campaign_id)

        applications = query.order_by(Application.created_at.desc()).paginate(page=page, per_page=per_page)

        return jsonify({
            'status': 'success',
            'data': [app.to_dict(include_details=True) for app in applications.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': applications.total,
                'pages': applications.pages
            }
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@applications_bp.route('/<int:application_id>', methods=['GET'])
@require_auth
def get_application(application_id, current_user):
    try:
        application = Application.query.get(application_id)
        if not application:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        # Check access
        role = current_user.get('role')
        user_id = current_user.get('user_id')
        if role == 'creator' and application.creator_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403
        if role == 'brand' and application.campaign.brand_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        return jsonify({'status': 'success', 'data': application.to_dict(include_details=True)}), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@applications_bp.route('', methods=['POST'])
@require_auth
def create_application(current_user):
    """Creator applies to a campaign"""
    try:
        if current_user.get('role') != 'creator':
            return jsonify({'status': 'error', 'message': 'Only creators can apply to campaigns'}), 403

        data = request.get_json()
        creator_id = current_user.get('user_id')

        campaign_id = data.get('campaign_id')
        proposed_rate = data.get('proposed_rate')

        if not campaign_id or not proposed_rate:
            return jsonify({'status': 'error', 'message': 'campaign_id and proposed_rate are required'}), 400

        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'status': 'error', 'message': 'Campaign not found'}), 404

        if campaign.status != 'active':
            return jsonify({'status': 'error', 'message': 'Campaign is not accepting applications'}), 400

        existing_app = Application.query.filter_by(
            campaign_id=campaign_id,
            creator_id=creator_id
        ).first()

        if existing_app:
            return jsonify({'status': 'error', 'message': 'You already applied to this campaign'}), 409

        application = Application(
            campaign_id=campaign_id,
            creator_id=creator_id,
            proposed_rate=float(proposed_rate),
            message=data.get('message'),
        )

        db.session.add(application)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Application submitted',
            'data': application.to_dict(include_details=True)
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500


@applications_bp.route('/<int:application_id>/respond', methods=['PUT'])
@require_auth
def respond_to_application(application_id, current_user):
    """Brand accepts or rejects an application"""
    try:
        if current_user.get('role') != 'brand':
            return jsonify({'status': 'error', 'message': 'Only brands can respond to applications'}), 403

        application = Application.query.get(application_id)
        if not application:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        # Verify brand owns the campaign
        if application.campaign.brand_id != current_user.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        if application.status != 'pending':
            return jsonify({'status': 'error', 'message': f'Application already {application.status}'}), 400

        data = request.get_json()
        action = data.get('action')

        if action not in ['accept', 'reject']:
            return jsonify({'status': 'error', 'message': 'Action must be "accept" or "reject"'}), 400

        application.status = 'accepted' if action == 'accept' else 'rejected'
        application.updated_at = datetime.utcnow()

        # If accepted, auto-create an accepted ContactRequest so they can message each other
        if application.status == 'accepted':
            brand_id = current_user.get('user_id')
            creator_id = application.creator_id
            existing_contact = ContactRequest.query.filter_by(
                brand_id=brand_id, creator_id=creator_id
            ).first()
            if not existing_contact:
                contact = ContactRequest(
                    brand_id=brand_id,
                    creator_id=creator_id,
                    status='accepted',
                    message='Auto-created from accepted campaign application',
                )
                db.session.add(contact)
            elif existing_contact.status != 'accepted':
                existing_contact.status = 'accepted'
                existing_contact.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'Application {application.status}',
            'data': application.to_dict(include_details=True)
        }), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500


@applications_bp.route('/my', methods=['GET'])
@require_auth
def get_my_applications(current_user):
    """Get all campaign IDs the current creator has applied to (quick lookup)"""
    try:
        if current_user.get('role') != 'creator':
            return jsonify({'status': 'error', 'message': 'Only creators can use this endpoint'}), 403

        creator_id = current_user.get('user_id')
        apps = Application.query.filter_by(creator_id=creator_id).all()

        return jsonify({
            'status': 'success',
            'data': [
                {
                    'campaign_id': a.campaign_id,
                    'status': a.status,
                    'id': a.id
                }
                for a in apps
            ]
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@applications_bp.route('/<int:application_id>', methods=['DELETE'])
@require_auth
def delete_application(application_id, current_user):
    """Creator withdraws their application"""
    try:
        application = Application.query.get(application_id)
        if not application:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        if current_user.get('role') != 'creator' or application.creator_id != current_user.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        db.session.delete(application)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Application withdrawn'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500
