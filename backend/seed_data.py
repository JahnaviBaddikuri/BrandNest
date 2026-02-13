from app import create_app, db
from models import Creator, Brand, Campaign, Application
from datetime import datetime, timedelta


def seed_database():
    
    app = create_app()
    
    with app.app_context():
        print("clearing")
        db.drop_all()
        db.create_all()
        
        print("creating creators")
        creators = [
            Creator(
                username='john_fashion',
                email='john@example.com',
                platform='instagram',
                followers_count=150000,
                engagement_rate=4.8,
                category='fashion',
                location='New York, USA',
                rate=500.0,
                bio='Fashion influencer from NYC',
                is_verified=True
            ),
            Creator(
                username='sarah_beauty',
                email='sarah@example.com',
                platform='instagram',
                followers_count=200000,
                engagement_rate=5.2,
                category='beauty',
                location='Los Angeles, USA',
                rate=750.0,
                bio='Beauty and makeup creator',
                is_verified=True
            ),
            Creator(
                username='mike_fitness',
                email='mike@example.com',
                platform='tiktok',
                followers_count=500000,
                engagement_rate=6.5,
                category='fitness',
                location='Miami, USA',
                rate=1000.0,
                bio='Fitness and gym content',
                is_verified=True
            ),
            Creator(
                username='emma_lifestyle',
                email='emma@example.com',
                platform='youtube',
                followers_count=300000,
                engagement_rate=4.2,
                category='lifestyle',
                location='London, UK',
                rate=600.0,
                bio='Lifestyle vlogger',
                is_verified=False
            ),
            Creator(
                username='david_tech',
                email='david@example.com',
                platform='instagram',
                followers_count=80000,
                engagement_rate=3.9,
                category='technology',
                location='San Francisco, USA',
                rate=400.0,
                bio='Tech gadget reviewer',
                is_verified=False
            ),
        ]
        
        for creator in creators:
            db.session.add(creator)
        
        db.session.commit()
        print(f"creators: {len(creators)}")
        
       
        print("creating brands...")
        brands = [
            Brand(
                company_name='Nike Inc',
                email='marketing@nike.com',
                industry='sports',
                location='Portland, OR, USA',
                website='https://www.nike.com',
                verified=True
            ),
            Brand(
                company_name='L\'Oreal Beauty',
                email='influencer@loreal.com',
                industry='beauty',
                location='Paris, France',
                website='https://www.loreal.com',
                verified=True
            ),
            Brand(
                company_name='Apple Inc',
                email='partnerships@apple.com',
                industry='technology',
                location='Cupertino, CA, USA',
                website='https://www.apple.com',
                verified=True
            ),
            Brand(
                company_name='Zara Fashion',
                email='brand@zara.com',
                industry='fashion',
                location='Barcelona, Spain',
                website='https://www.zara.com',
                verified=False
            ),
        ]
        
        for brand in brands:
            db.session.add(brand)
        
        db.session.commit()
        print(f"brands: {len(brands)}")

        print("creating campaigns...")
        campaigns = [
            Campaign(
                brand_id=1,
                title='Nike Summer Collection Campaign',
                description='Promote new summer athletic wear collection',
                budget=100000.0,
                target_platform='instagram',
                target_category='fitness',
                min_followers=50000,
                max_budget_per_creator=5000.0,
                status='active',
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30)
            ),
            Campaign(
                brand_id=2,
                title='L\'Oreal Beauty Challenge',
                description='Create content showcasing our new makeup line',
                budget=80000.0,
                target_platform='tiktok',
                target_category='beauty',
                min_followers=100000,
                max_budget_per_creator=4000.0,
                status='active',
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=45)
            ),
            Campaign(
                brand_id=3,
                title='Apple Tech Review Campaign',
                description='Review and demo new iPhone features',
                budget=150000.0,
                target_platform='youtube',
                target_category='technology',
                min_followers=50000,
                max_budget_per_creator=8000.0,
                status='active',
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=60)
            ),
            Campaign(
                brand_id=4,
                title='Zara Fashion Week',
                description='Fashion week collection showcase',
                budget=120000.0,
                target_platform='instagram',
                target_category='fashion',
                min_followers=100000,
                max_budget_per_creator=6000.0,
                status='draft',
                start_date=datetime.now() + timedelta(days=30),
                end_date=datetime.now() + timedelta(days=90)
            ),
        ]

        for campaign in campaigns:
            db.session.add(campaign)

        db.session.commit()
        print(f"campaigns: {len(campaigns)}")

        print("creating applications...")
        applications = [
            Application(
                campaign_id=1,
                creator_id=3,
                proposed_rate=2500.0,
                status='pending',
                message='I would love to promote Nike\'s athletic wear!'
            ),
            Application(
                campaign_id=2,
                creator_id=2,
                proposed_rate=2000.0,
                status='accepted',
                message='Perfect! Beauty is my passion!'
            ),
            Application(
                campaign_id=3,
                creator_id=5,
                proposed_rate=4000.0,
                status='pending',
                message='Tech reviews are my specialty!'
            ),
            Application(
                campaign_id=1,
                creator_id=1,
                proposed_rate=3000.0,
                status='rejected',
                message='Fashion with function!'
            ),
        ]

        for application in applications:
            db.session.add(application)

        db.session.commit()
        print(f"applications: {len(applications)}")
        
        print("done!")


if __name__ == '__main__':
    try:
        seed_database()
    except Exception as error:
        print(f"error: {str(error)}")
        import traceback
        traceback.print_exc()
