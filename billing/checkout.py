"""
Stripe Checkout Session creation.
$0.02 per credit, minimum 250 credits ($5).
"""

import os

import stripe
from fastapi import HTTPException
from pydantic import BaseModel
from config import settings

CREDITS_PRICE_CENTS = int(os.getenv("CREDITS_PRICE_CENTS", 2))  # $0.02 per credit
MIN_CREDITS = int(os.getenv("MIN_CREDITS", 250))         # $5 minimum — keeps Stripe fees from dominating


class CheckoutRequest(BaseModel):
    credits: int
    user_id: str | None = None  # override used by the internal web proxy


def create_checkout_session(user_id: str, credits: int) -> str:
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing not configured.")

    if credits < MIN_CREDITS:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum purchase is {MIN_CREDITS} credits (${MIN_CREDITS * CREDITS_PRICE_CENTS / 100:.0f}).",
        )

    stripe.api_key = settings.STRIPE_SECRET_KEY
    amount_cents = credits * CREDITS_PRICE_CENTS

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": amount_cents,
                "product_data": {
                    "name": f"{credits} Snipex Credits",
                    "description": f"{credits} API requests at $0.02 each",
                },
            },
            "quantity": 1,
        }],
        metadata={"user_id": user_id, "credits": str(credits)},
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    return session.url
