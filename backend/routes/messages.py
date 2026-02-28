# messaging routes

from flask import Blueprint, request, jsonify
from models import db, Message, Creator, Brand, ContactRequest
from jwt_auth import require_auth
from datetime import datetime

messages_bp = Blueprint('messages', __name__, url_prefix='/api/messages')


def get_user_name(role, user_id):
    """Get display name for a user"""
    if role == 'brand':
        brand = Brand.query.get(user_id)
        return brand.company_name if brand else 'Unknown'
    else:
        creator = Creator.query.get(user_id)
        return creator.username if creator else 'Unknown'


def get_user_image(role, user_id):
    """Get profile image for a user"""
    if role == 'brand':
        brand = Brand.query.get(user_id)
        return brand.logo_url if brand else None
    else:
        creator = Creator.query.get(user_id)
        return creator.profile_image_url if creator else None


@messages_bp.route('/conversations', methods=['GET'])
@require_auth
def get_conversations(current_user):
    """Get all conversations for the current user (grouped by other party)"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        # Get all messages where user is sender or receiver
        sent = Message.query.filter_by(sender_role=role, sender_id=user_id)
        received = Message.query.filter_by(receiver_role=role, receiver_id=user_id)
        all_messages = sent.union(received).order_by(Message.created_at.desc()).all()

        # Group by conversation partner
        conversations = {}
        for msg in all_messages:
            if msg.sender_role == role and msg.sender_id == user_id:
                partner_key = f"{msg.receiver_role}_{msg.receiver_id}"
                partner_role = msg.receiver_role
                partner_id = msg.receiver_id
            else:
                partner_key = f"{msg.sender_role}_{msg.sender_id}"
                partner_role = msg.sender_role
                partner_id = msg.sender_id

            if partner_key not in conversations:
                conversations[partner_key] = {
                    'partner_role': partner_role,
                    'partner_id': partner_id,
                    'partner_name': get_user_name(partner_role, partner_id),
                    'partner_image': get_user_image(partner_role, partner_id),
                    'last_message': msg.content[:100],
                    'last_message_time': msg.created_at.isoformat(),
                    'unread_count': 0,
                }
            
            # Count unread messages from this partner
            if msg.receiver_role == role and msg.receiver_id == user_id and not msg.is_read:
                conversations[partner_key]['unread_count'] += 1

        return jsonify({
            'status': 'success',
            'data': list(conversations.values())
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@messages_bp.route('/<partner_role>/<int:partner_id>', methods=['GET'])
@require_auth
def get_messages(partner_role, partner_id, current_user):
    """Get messages between current user and a specific partner"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        if partner_role not in ['brand', 'creator']:
            return jsonify({'status': 'error', 'message': 'Invalid partner role'}), 400

        # Verify they have an accepted contact request between them
        if role == 'brand' and partner_role == 'creator':
            contact = ContactRequest.query.filter_by(brand_id=user_id, creator_id=partner_id, status='accepted').first()
        elif role == 'creator' and partner_role == 'brand':
            contact = ContactRequest.query.filter_by(brand_id=partner_id, creator_id=user_id, status='accepted').first()
        else:
            contact = None

        if not contact:
            return jsonify({'status': 'error', 'message': 'You must have an accepted contact request to message this user'}), 403

        # Get messages in both directions
        sent = Message.query.filter_by(
            sender_role=role, sender_id=user_id,
            receiver_role=partner_role, receiver_id=partner_id
        )
        received = Message.query.filter_by(
            sender_role=partner_role, sender_id=partner_id,
            receiver_role=role, receiver_id=user_id
        )
        
        messages = sent.union(received).order_by(Message.created_at.asc()).all()

        # Mark received messages as read
        unread = Message.query.filter_by(
            sender_role=partner_role, sender_id=partner_id,
            receiver_role=role, receiver_id=user_id,
            is_read=False
        ).all()
        for msg in unread:
            msg.is_read = True
        db.session.commit()

        return jsonify({
            'status': 'success',
            'data': [msg.to_dict() for msg in messages]
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@messages_bp.route('', methods=['POST'])
@require_auth
def send_message(current_user):
    """Send a message to another user"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')
        data = request.get_json()

        receiver_role = data.get('receiver_role')
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()

        if not receiver_role or not receiver_id or not content:
            return jsonify({'status': 'error', 'message': 'receiver_role, receiver_id, and content are required'}), 400

        if receiver_role not in ['brand', 'creator']:
            return jsonify({'status': 'error', 'message': 'Invalid receiver role'}), 400

        # Verify accepted contact request exists
        if role == 'brand' and receiver_role == 'creator':
            contact = ContactRequest.query.filter_by(brand_id=user_id, creator_id=receiver_id, status='accepted').first()
        elif role == 'creator' and receiver_role == 'brand':
            contact = ContactRequest.query.filter_by(brand_id=receiver_id, creator_id=user_id, status='accepted').first()
        else:
            contact = None

        if not contact:
            return jsonify({'status': 'error', 'message': 'You must have an accepted contact request to message this user'}), 403

        message = Message(
            sender_role=role,
            sender_id=user_id,
            receiver_role=receiver_role,
            receiver_id=receiver_id,
            content=content,
        )

        db.session.add(message)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Message sent',
            'data': message.to_dict()
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500


@messages_bp.route('/contacts', methods=['GET'])
@require_auth
def get_messageable_contacts(current_user):
    """Get all users this user can message (accepted contact requests)"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        if role == 'brand':
            contacts = ContactRequest.query.filter_by(brand_id=user_id, status='accepted').all()
            result = []
            for c in contacts:
                creator = Creator.query.get(c.creator_id)
                if creator:
                    result.append({
                        'partner_role': 'creator',
                        'partner_id': creator.id,
                        'partner_name': creator.username,
                        'partner_image': creator.profile_image_url,
                    })
        else:
            contacts = ContactRequest.query.filter_by(creator_id=user_id, status='accepted').all()
            result = []
            for c in contacts:
                brand = Brand.query.get(c.brand_id)
                if brand:
                    result.append({
                        'partner_role': 'brand',
                        'partner_id': brand.id,
                        'partner_name': brand.company_name,
                        'partner_image': brand.logo_url,
                    })

        return jsonify({
            'status': 'success',
            'data': result
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@messages_bp.route('/unread-count', methods=['GET'])
@require_auth
def get_unread_count(current_user):
    """Get total unread message count"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        count = Message.query.filter_by(
            receiver_role=role,
            receiver_id=user_id,
            is_read=False
        ).count()

        return jsonify({
            'status': 'success',
            'data': {'unread_count': count}
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500
