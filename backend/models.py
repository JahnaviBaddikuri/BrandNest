from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from password_utils import hash_password, verify_password

db = SQLAlchemy()


class Creator(db.Model):
    __tablename__ = 'creators'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(50), nullable=False, default='instagram')
    followers_count = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    rate = db.Column(db.Float, nullable=False)
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.String(500))
    is_verified = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    otp_code = db.Column(db.String(10), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return verify_password(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        """
        Convert model to dictionary
        Args:
            include_sensitive: If True, includes password_hash (use with caution!)
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'platform': self.platform,
            'followers_count': self.followers_count,
            'engagement_rate': self.engagement_rate,
            'category': self.category,
            'location': self.location,
            'rate': self.rate,
            'bio': self.bio,
            'profile_image_url': self.profile_image_url,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        # Never include password hash in normal responses
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data

    def __repr__(self):
        return f'<Creator {self.username}>'


class Brand(db.Model):
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    website = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))
    verified = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    otp_code = db.Column(db.String(10), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return verify_password(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        """
        Convert model to dictionary
        Args:
            include_sensitive: If True, includes password_hash (use with caution!)
        """
        data = {
            'id': self.id,
            'company_name': self.company_name,
            'email': self.email,
            'industry': self.industry,
            'location': self.location,
            'website': self.website,
            'logo_url': self.logo_url,
            'verified': self.verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        # Never include password hash in normal responses
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data

    def __repr__(self):
        return f'<Brand {self.company_name}>'


class ContactRequest(db.Model):
    __tablename__ = 'contact_requests'

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('creators.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = db.relationship('Brand', backref='contact_requests_sent', foreign_keys=[brand_id])
    creator = db.relationship('Creator', backref='contact_requests_received', foreign_keys=[creator_id])

    # Prevent duplicate requests from same brand to same creator
    __table_args__ = (db.UniqueConstraint('brand_id', 'creator_id', name='unique_brand_creator_request'),)

    def to_dict(self, include_details=False):
        """
        Convert model to dictionary
        Args:
            include_details: If True, includes brand and creator details
        """
        data = {
            'id': self.id,
            'brand_id': self.brand_id,
            'creator_id': self.creator_id,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        
        if include_details:
            # Add brand and creator basic info
            data['brand'] = {
                'id': self.brand.id,
                'company_name': self.brand.company_name,
                'logo_url': self.brand.logo_url,
                'industry': self.brand.industry,
            }
            data['creator'] = {
                'id': self.creator.id,
                'username': self.creator.username,
                'profile_image_url': self.creator.profile_image_url,
                'platform': self.creator.platform,
                'category': self.creator.category,
            }
            
            # Include contact info only if request is accepted
            if self.status == 'accepted':
                data['brand']['email'] = self.brand.email
                data['brand']['website'] = self.brand.website
                data['creator']['email'] = self.creator.email
        
        return data

    def __repr__(self):
        return f'<ContactRequest brand={self.brand_id} creator={self.creator_id} status={self.status}>'


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float)
    target_platform = db.Column(db.String(50))
    target_category = db.Column(db.String(100))
    min_followers = db.Column(db.Integer, default=0)
    max_budget_per_creator = db.Column(db.Float)
    status = db.Column(db.String(50), default='active')  # active, paused, completed, cancelled
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = db.relationship('Brand', backref='campaigns', foreign_keys=[brand_id])

    def to_dict(self, include_brand=False):
        data = {
            'id': self.id,
            'brand_id': self.brand_id,
            'title': self.title,
            'description': self.description,
            'budget': self.budget,
            'target_platform': self.target_platform,
            'target_category': self.target_category,
            'min_followers': self.min_followers,
            'max_budget_per_creator': self.max_budget_per_creator,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        if include_brand and self.brand:
            data['brand'] = {
                'id': self.brand.id,
                'company_name': self.brand.company_name,
                'logo_url': self.brand.logo_url,
                'industry': self.brand.industry,
            }
        return data

    def __repr__(self):
        return f'<Campaign {self.title}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('creators.id'), nullable=False)
    proposed_rate = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaign = db.relationship('Campaign', backref='applications', foreign_keys=[campaign_id])
    creator = db.relationship('Creator', backref='applications', foreign_keys=[creator_id])

    __table_args__ = (db.UniqueConstraint('campaign_id', 'creator_id', name='unique_campaign_creator_app'),)

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'creator_id': self.creator_id,
            'proposed_rate': self.proposed_rate,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        if include_details:
            if self.campaign:
                data['campaign'] = {
                    'id': self.campaign.id,
                    'title': self.campaign.title,
                    'budget': self.campaign.budget,
                    'target_platform': self.campaign.target_platform,
                }
            if self.creator:
                data['creator'] = {
                    'id': self.creator.id,
                    'username': self.creator.username,
                    'profile_image_url': self.creator.profile_image_url,
                    'platform': self.creator.platform,
                    'rate': self.creator.rate,
                }
        return data

    def __repr__(self):
        return f'<Application campaign={self.campaign_id} creator={self.creator_id}>'


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_role = db.Column(db.String(20), nullable=False)  # 'brand' or 'creator'
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_role = db.Column(db.String(20), nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sender_role': self.sender_role,
            'sender_id': self.sender_id,
            'receiver_role': self.receiver_role,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_role}:{self.sender_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_role = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # contact_request, message, application, order, review
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(500))  # optional: page to navigate to
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_role': self.user_role,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'body': self.body,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Notification {self.id} for {self.user_role}:{self.user_id}>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('creators.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    deliverables = db.Column(db.Text)  # JSON string of deliverable items
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, in_progress, delivered, revision, completed, cancelled
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = db.relationship('Brand', backref='orders_placed', foreign_keys=[brand_id])
    creator = db.relationship('Creator', backref='orders_received', foreign_keys=[creator_id])
    campaign = db.relationship('Campaign', backref='orders', foreign_keys=[campaign_id])

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'brand_id': self.brand_id,
            'creator_id': self.creator_id,
            'campaign_id': self.campaign_id,
            'title': self.title,
            'description': self.description,
            'deliverables': self.deliverables,
            'price': self.price,
            'status': self.status,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        if include_details:
            if self.brand:
                data['brand'] = {
                    'id': self.brand.id,
                    'company_name': self.brand.company_name,
                    'logo_url': self.brand.logo_url,
                }
            if self.creator:
                data['creator'] = {
                    'id': self.creator.id,
                    'username': self.creator.username,
                    'profile_image_url': self.creator.profile_image_url,
                }
        return data

    def __repr__(self):
        return f'<Order {self.id} {self.status}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    reviewer_role = db.Column(db.String(20), nullable=False)  # 'brand' or 'creator'
    reviewer_id = db.Column(db.Integer, nullable=False)
    reviewee_role = db.Column(db.String(20), nullable=False)
    reviewee_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1.0 to 5.0
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order = db.relationship('Order', backref='reviews', foreign_keys=[order_id])

    __table_args__ = (db.UniqueConstraint('order_id', 'reviewer_role', 'reviewer_id', name='unique_order_reviewer'),)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'reviewer_role': self.reviewer_role,
            'reviewer_id': self.reviewer_id,
            'reviewee_role': self.reviewee_role,
            'reviewee_id': self.reviewee_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Review {self.id} rating={self.rating}>'
