# applications routes

from flask import Blueprint, request, jsonify
from models import db, Application, Campaign, Creator
from datetime import datetime

applications_bp = Blueprint('applications', __name__, url_prefix='/api/applications')


@applications_bp.route('', methods=['GET'])
def get_applications():
    # list applications
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', type=str)
        creator_id = request.args.get('creator_id', type=int)
        campaign_id = request.args.get('campaign_id', type=int)

        query = Application.query
        if status:
            query = query.filter_by(status=status)
        if creator_id:
            query = query.filter_by(creator_id=creator_id)
        if campaign_id:
            query = query.filter_by(campaign_id=campaign_id)

        applications = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'status': 'success',
            'data': [app.to_dict() for app in applications.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': applications.total,
                'pages': applications.pages
            }
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': 'error'}), 500


@applications_bp.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    # get application
    try:
        application = Application.query.get(application_id)
        if not application:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        return jsonify({'status': 'success', 'data': application.to_dict()}), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': 'error'}), 500


@applications_bp.route('', methods=['POST'])
def create_application():
    # create application
    try:
        data = request.get_json()

        required = ['campaign_id', 'creator_id', 'proposed_rate']
        missing = [f for f in required if not data.get(f)]

        if missing:
            return jsonify({'status': 'error', 'message': f'missing: {", ".join(missing)}'}), 400

        campaign = Campaign.query.get(data['campaign_id'])
        if not campaign:
            return jsonify({'status': 'error', 'message': 'campaign not found'}), 404

        creator = Creator.query.get(data['creator_id'])
        if not creator:
            return jsonify({'status': 'error', 'message': 'creator not found'}), 404

        existing_app = Application.query.filter_by(
            campaign_id=data['campaign_id'],
            creator_id=data['creator_id']
        ).first()

        if existing_app:
            return jsonify({'status': 'error', 'message': 'already applied'}), 400

        application = Application(
            campaign_id=data['campaign_id'],
            creator_id=data['creator_id'],
            proposed_rate=data['proposed_rate'],
            message=data.get('message'),
        )

        db.session.add(application)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'created',
            'data': application.to_dict()
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500


@applications_bp.route('/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    # update application
    try:
        application = Application.query.get(application_id)
        if not application:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        data = request.get_json()

        if 'status' in data:
            valid = ['pending', 'accepted', 'rejected']
            if data['status'] not in valid:
                return jsonify({'status': 'error', 'message': 'bad status'}), 400
            application.status = data['status']

        if 'message' in data:
            application.message = data['message']

        application.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'updated',
            'data': application.to_dict()
        }), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500


@applications_bp.route('/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    # delete application
    try:
        application = Application.query.get(application_id)
        if not application:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        db.session.delete(application)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'deleted'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'error'}), 500
