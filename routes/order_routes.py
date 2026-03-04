from flask import Blueprint, request, redirect, jsonify
import re
import requests
import os

from extensions import db
from models import Product, Order

order_bp = Blueprint("order_bp", __name__)

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://127.0.0.1:5000")


@order_bp.route("/create-order/<int:product_id>", methods=["POST"])
def create_order(product_id):

    email = (request.form.get("email") or '').strip()
    custom_amount = request.form.get("amount")

    product = Product.query.get_or_404(product_id)

    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return "Invalid email address", 400

    try:
        amount_float = float(custom_amount) if custom_amount else product.price
    except:
        return "Invalid amount", 400

    order = Order(
        customer_email=email,
        product_id=product.id,
        status="pending"
    )

    db.session.add(order)
    db.session.commit()

    amount = int(amount_float * 100)

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": amount,
        "reference": f"SMARTSORT_{order.id}",
        "callback_url": f"{PUBLIC_URL}/verify-payment"
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=data,
        headers=headers
    )

    response_data = response.json()

    if response_data["status"]:
        order.payment_reference = data["reference"]
        db.session.commit()

        return redirect(response_data["data"]["authorization_url"])

    return "Payment initialization failed", 500