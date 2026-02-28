from flask import Blueprint, request, jsonify
from models import db, ContactRequest, Brand, Creator
from jwt_auth import require_auth
from datetime import datetime

contact_requests_bp = Blueprint('contact_requests', __name__, url_prefix='/api')


@contact_requests_bp.route('/contact-requests', methods=['POST'])
@require_auth
def send_contact_request(current_user):
    """Brand sends contact request to creator"""
    try:
        data = request.get_json()
        token_data = current_user
        
        # Verify requester is a brand
        if token_data.get('role') != 'brand':
            return jsonify({'error': 'Only brands can send contact requests'}), 403
        
        brand_id = token_data.get('user_id')
        creator_id = data.get('creator_id')
        message = data.get('message', '')
        
        if not creator_id:
            return jsonify({'error': 'Creator ID is required'}), 400
        
        # Check if creator exists
        creator = Creator.query.get(creator_id)
        if not creator:
            return jsonify({'error': 'Creator not found'}), 404
        
        # Check if request already exists
        existing_request = ContactRequest.query.filter_by(
            brand_id=brand_id,
            creator_id=creator_id
        ).first()
        
        if existing_request:
            return jsonify({
                'error': 'You already sent a request to this creator',
                'existing_request': existing_request.to_dict(include_details=True)
            }), 409
        
        # Create new contact request
        contact_request = ContactRequest(
            brand_id=brand_id,
            creator_id=creator_id,
            message=message,
            status='pending'
        )
        
        db.session.add(contact_request)
        db.session.commit()
        
        return jsonify({
            'message': 'Contact request sent successfully',
            'request': contact_request.to_dict(include_details=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@contact_requests_bp.route('/contact-requests', methods=['GET'])
@require_auth
def get_contact_requests(current_user):
    """Get contact requests - brands see sent, creators see received"""
    try:
        token_data = current_user
        role = token_data.get('role')
        user_id = token_data.get('user_id')
        
        # Get status filter if provided
        status = request.args.get('status')
        
        if role == 'brand':
            # Brands see requests they sent
            query = ContactRequest.query.filter_by(brand_id=user_id)
        elif role == 'creator':
            # Creators see requests they received
            query = ContactRequest.query.filter_by(creator_id=user_id)
        else:
            return jsonify({'error': 'Invalid role'}), 403
        
        # Apply status filter if provided
        if status:
            query = query.filter_by(status=status)
        
        # Get all requests
        requests = query.order_by(ContactRequest.created_at.desc()).all()
        
        return jsonify({
            'requests': [req.to_dict(include_details=True) for req in requests],
            'count': len(requests)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contact_requests_bp.route('/contact-requests/<int:request_id>', methods=['GET'])
@require_auth
def get_contact_request(request_id, current_user):
    """Get single contact request details"""
    try:
        token_data = current_user
        role = token_data.get('role')
        user_id = token_data.get('user_id')
        
        contact_request = ContactRequest.query.get(request_id)
        
        if not contact_request:
            return jsonify({'error': 'Contact request not found'}), 404
        
        # Check if user has permission to view this request
        if role == 'brand' and contact_request.brand_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        elif role == 'creator' and contact_request.creator_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'request': contact_request.to_dict(include_details=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contact_requests_bp.route('/contact-requests/<int:request_id>/respond', methods=['PUT'])
@require_auth
def respond_to_request(request_id, current_user):
    """Creator accepts or rejects contact request"""
    try:
        data = request.get_json()
        token_data = current_user
        
        # Verify requester is a creator
        if token_data.get('role') != 'creator':
            return jsonify({'error': 'Only creators can respond to contact requests'}), 403
        
        creator_id = token_data.get('user_id')
        action = data.get('action')  # 'accept' or 'reject'
        
        if action not in ['accept', 'reject']:
            return jsonify({'error': 'Action must be "accept" or "reject"'}), 400
        
        # Get the contact request
        contact_request = ContactRequest.query.get(request_id)
        
        if not contact_request:
            return jsonify({'error': 'Contact request not found'}), 404
        
        # Verify this request is for the current creator
        if contact_request.creator_id != creator_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if already responded
        if contact_request.status != 'pending':
            return jsonify({
                'error': f'Request already {contact_request.status}',
                'request': contact_request.to_dict(include_details=True)
            }), 400
        
        # Update status
        contact_request.status = 'accepted' if action == 'accept' else 'rejected'
        contact_request.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Contact request {contact_request.status}',
            'request': contact_request.to_dict(include_details=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
