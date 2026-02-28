# review routes

from flask import Blueprint, request, jsonify
from models import db, Review, Order, Creator, Brand
from jwt_auth import require_auth
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')


@reviews_bp.route('', methods=['POST'])
@require_auth
def create_review(current_user):
    """Create a review for a completed order"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')
        data = request.get_json()

        order_id = data.get('order_id')
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not order_id or rating is None:
            return jsonify({'status': 'error', 'message': 'order_id and rating are required'}), 400

        rating = float(rating)
        if rating < 1.0 or rating > 5.0:
            return jsonify({'status': 'error', 'message': 'Rating must be between 1.0 and 5.0'}), 400

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404

        if order.status != 'completed':
            return jsonify({'status': 'error', 'message': 'Can only review completed orders'}), 400

        # Determine reviewer and reviewee
        if role == 'brand' and order.brand_id == user_id:
            reviewee_role = 'creator'
            reviewee_id = order.creator_id
        elif role == 'creator' and order.creator_id == user_id:
            reviewee_role = 'brand'
            reviewee_id = order.brand_id
        else:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        # Check for duplicate review
        existing = Review.query.filter_by(
            order_id=order_id,
            reviewer_role=role,
            reviewer_id=user_id
        ).first()
        if existing:
            return jsonify({'status': 'error', 'message': 'You already reviewed this order'}), 409

        review = Review(
            order_id=order_id,
            reviewer_role=role,
            reviewer_id=user_id,
            reviewee_role=reviewee_role,
            reviewee_id=reviewee_id,
            rating=rating,
            comment=comment,
        )

        db.session.add(review)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Review submitted',
            'data': review.to_dict()
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)}), 500


@reviews_bp.route('/user/<role>/<int:user_id>', methods=['GET'])
def get_user_reviews(role, user_id):
    """Get all reviews for a specific user (public)"""
    try:
        if role not in ['brand', 'creator']:
            return jsonify({'status': 'error', 'message': 'Invalid role'}), 400

        reviews = Review.query.filter_by(
            reviewee_role=role,
            reviewee_id=user_id
        ).order_by(Review.created_at.desc()).all()

        # Calculate average rating
        avg_rating = 0
        if reviews:
            avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

        # Enrich with reviewer names
        review_data = []
        for r in reviews:
            rd = r.to_dict()
            if r.reviewer_role == 'brand':
                brand = Brand.query.get(r.reviewer_id)
                rd['reviewer_name'] = brand.company_name if brand else 'Unknown'
            else:
                creator = Creator.query.get(r.reviewer_id)
                rd['reviewer_name'] = creator.username if creator else 'Unknown'
            review_data.append(rd)

        return jsonify({
            'status': 'success',
            'data': {
                'reviews': review_data,
                'count': len(reviews),
                'average_rating': avg_rating,
            }
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


@reviews_bp.route('/order/<int:order_id>', methods=['GET'])
@require_auth
def get_order_reviews(order_id, current_user):
    """Get reviews for a specific order"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404

        if role == 'brand' and order.brand_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403
        if role == 'creator' and order.creator_id != user_id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

        reviews = Review.query.filter_by(order_id=order_id).all()

        return jsonify({
            'status': 'success',
            'data': [r.to_dict() for r in reviews]
        }), 200

    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500
