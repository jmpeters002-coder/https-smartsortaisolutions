from flask import Blueprint, request, redirect, jsonify, render_template
import requests
import os
import hmac
import hashlib

from extensions import db
from models import Order, UserAccess
from flask_mail import Message

from flask import Blueprint, request, redirect, jsonify
payment_bp = Blueprint("payment_bp", __name__)

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://127.0.0.1:5000")


def verify_paystack_signature(payload, signature):
    computed = hmac.new(
        PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    return hmac.compare_digest(computed, signature)


@payment_bp.route("/webhook", methods=["POST"])
def paystack_webhook():

    payload = request.get_data()
    signature = request.headers.get("x-paystack-signature")

    if not verify_paystack_signature(payload, signature):
        return "Invalid signature", 400

    event = request.json

    if event.get("event") == "charge.success":

        reference = event["data"]["reference"]

        order = Order.query.filter_by(
            payment_reference=reference
        ).first()

        if order and order.status != "paid":
            order.status = "paid"
            db.session.commit()

    return "OK", 200
@payment_bp.route("/verify-payment")
def verify_payment():

    reference = request.args.get("reference")

    if not reference:
        return "Reference not provided", 400

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }
