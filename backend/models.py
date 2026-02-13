from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Creator(db.Model):
    __tablename__ = 'creators'

    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False, index=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    platform = db.Column(db.String(50), nullable=False, default='instagram')
    followers_count = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    rate = db.Column(db.Float, nullable=False)
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.String(500))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = db.relationship('Application', backref='creator', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'firebase_uid': self.firebase_uid,
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

    def __repr__(self):
        return f'<Creator {self.username}>'


class Brand(db.Model):
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    website = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaigns = db.relationship('Campaign', backref='brand', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'firebase_uid': self.firebase_uid,
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

    def __repr__(self):
        return f'<Brand {self.company_name}>'


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    target_platform = db.Column(db.String(50), nullable=False)
    target_category = db.Column(db.String(100))
    min_followers = db.Column(db.Integer, default=0)
    max_budget_per_creator = db.Column(db.Float)
    status = db.Column(db.String(50), default='active')
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = db.relationship('Application', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
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
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f'<Campaign {self.title}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('creators.id'), nullable=False)
    proposed_rate = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'creator_id': self.creator_id,
            'proposed_rate': self.proposed_rate,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f'<Application {self.id}>'
