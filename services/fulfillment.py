from extensions import db
from models import UserAccess


def fulfill_order(order):

    existing_access = UserAccess.query.filter_by(
        customer_email=order.customer_email,
        product_id=order.product_id
    ).first()

    if existing_access:
        return

    access = UserAccess(
        customer_email=order.customer_email,
        product_id=order.product_id,
        order_id=order.id,
        access_type=order.product.product_type
    )

    db.session.add(access)
    db.session.commit()

    print(f"✅ Access granted: {order.customer_email}")