from models.order import Order
from extensions import db

def confirm_payment(order_id, payment_reference):
    order = Order.query.get(order_id)
    if not order:
        raise ValueError("Order not found")
    
    if order.status == "paid":
        return order  # Already processed
    
    if order.payment_reference != payment_reference:
        raise ValueError("Invalid payment reference")
    
    order.status = "paid"
    db.session.commit()
    
    return order