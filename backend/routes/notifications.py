# notification routes

from flask import Blueprint, request, jsonify
from models import db, Notification
from jwt_auth import require_auth
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


def create_notification(user_role, user_id, notif_type, title, body=None, link=None):
    """Helper to create a notification from anywhere in the app"""
    try:
        notif = Notification(
            user_role=user_role,
            user_id=user_id,
            type=notif_type,
            title=title,
            body=body,
            link=link,
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    except Exception:
        db.session.rollback()
        return None


@notifications_bp.route('', methods=['GET'])
@require_auth
def get_notifications(current_user):
    """Get notifications for the current user"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')
        unread_only = request.args.get('unread', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)

        query = Notification.query.filter_by(user_role=role, user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)

        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

        return jsonify({
            'status': 'success',
            'data': [n.to_dict() for n in notifications]
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@notifications_bp.route('/unread-count', methods=['GET'])
@require_auth
def get_unread_count(current_user):
    """Get unread notification count"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        count = Notification.query.filter_by(
            user_role=role,
            user_id=user_id,
            is_read=False
        ).count()

        return jsonify({
            'status': 'success',
            'data': {'unread_count': count}
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@require_auth
def mark_as_read(notification_id, current_user):
    """Mark a notification as read"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        notif = Notification.query.get(notification_id)
        if not notif:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        if notif.user_role != role or notif.user_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        notif.is_read = True
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Marked as read'}), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@notifications_bp.route('/read-all', methods=['PUT'])
@require_auth
def mark_all_as_read(current_user):
    """Mark all notifications as read"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        Notification.query.filter_by(
            user_role=role,
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'All marked as read'}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500
