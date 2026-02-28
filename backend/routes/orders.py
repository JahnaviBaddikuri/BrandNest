# order/collaboration routes

from flask import Blueprint, request, jsonify
from models import db, Order, Brand, Creator, Campaign
from jwt_auth import require_auth
from datetime import datetime
import json

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@orders_bp.route('', methods=['GET'])
@require_auth
def get_orders(current_user):
    """Get orders for current user"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')
        status = request.args.get('status', type=str)

        if role == 'brand':
            query = Order.query.filter_by(brand_id=user_id)
        elif role == 'creator':
            query = Order.query.filter_by(creator_id=user_id)
        else:
            return jsonify({'status': 'error', 'message': 'Invalid role'}), 403

        if status:
            query = query.filter_by(status=status)

        orders = query.order_by(Order.created_at.desc()).all()

        return jsonify({
            'status': 'success',
            'data': [o.to_dict(include_details=True) for o in orders]
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@orders_bp.route('/<int:order_id>', methods=['GET'])
@require_auth
def get_order(order_id, current_user):
    """Get a single order"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        if role == 'brand' and order.brand_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403
        if role == 'creator' and order.creator_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        return jsonify({'status': 'success', 'data': order.to_dict(include_details=True)}), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@orders_bp.route('', methods=['POST'])
@require_auth
def create_order(current_user):
    """Brand creates an order"""
    try:
        if current_user.get('role') != 'brand':
            return jsonify({'status': 'error', 'message': 'Only brands can create orders'}), 403

        data = request.get_json()
        brand_id = current_user.get('user_id')

        required = ['creator_id', 'title', 'price']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({'status': 'error', 'message': f'Missing: {", ".join(missing)}'}), 400

        creator = Creator.query.get(data['creator_id'])
        if not creator:
            return jsonify({'status': 'error', 'message': 'Creator not found'}), 404

        deliverables = data.get('deliverables', '')
        if isinstance(deliverables, list):
            deliverables = json.dumps(deliverables)

        order = Order(
            brand_id=brand_id,
            creator_id=data['creator_id'],
            campaign_id=data.get('campaign_id'),
            title=data['title'],
            description=data.get('description', ''),
            deliverables=deliverables,
            price=float(data['price']),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
        )

        db.session.add(order)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Order created',
            'data': order.to_dict(include_details=True)
        }), 201

    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid date format'}), 400
    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500


@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@require_auth
def update_order_status(order_id, current_user):
    """Update order status"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'status': 'error', 'message': 'not found'}), 404

        # Verify access
        if role == 'brand' and order.brand_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403
        if role == 'creator' and order.creator_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        data = request.get_json()
        new_status = data.get('status')

        valid_statuses = ['pending', 'accepted', 'in_progress', 'delivered', 'revision', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'status': 'error', 'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

        # Validate status transitions based on role
        brand_allowed = ['completed', 'revision', 'cancelled']
        creator_allowed = ['accepted', 'in_progress', 'delivered', 'cancelled']

        if role == 'brand' and new_status not in brand_allowed:
            return jsonify({'status': 'error', 'message': f'Brands can only set status to: {", ".join(brand_allowed)}'}), 403
        if role == 'creator' and new_status not in creator_allowed:
            return jsonify({'status': 'error', 'message': f'Creators can only set status to: {", ".join(creator_allowed)}'}), 403

        order.status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'Order status updated to {new_status}',
            'data': order.to_dict(include_details=True)
        }), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500
