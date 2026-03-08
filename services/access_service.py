from models.user_access import UserAccess
from extensions import db

def grant_user_access(customer_email, product_id, order_id, access_type):
    # Check if access already exists
    existing = UserAccess.query.filter_by(
        customer_email=customer_email,
        product_id=product_id
    ).first()
    
    if existing:
        return existing  # Already granted
    
    access = UserAccess(
        customer_email=customer_email,
        product_id=product_id,
        order_id=order_id,
        access_type=access_type
    )
    db.session.add(access)
    db.session.commit()
    return access