"""
Stripe webhook handler.
Listens for checkout.session.completed and tops up user credits in Supabase.

The endpoint must be public (no Bearer auth) — Stripe calls it directly.
Verified via Stripe-Signature header instead.
"""

import logging
import stripe
from fastapi import HTTPException, Request
from config import settings

logger = logging.getLogger(__name__)


async def handle_webhook(request: Request) -> dict:
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Billing not configured.")

    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature.")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session["metadata"].to_dict() if session["metadata"] else {}
        user_id = metadata.get("user_id")
        credits = metadata.get("credits")
        if session["payment_status"] == "paid" and user_id and credits:
            _add_credits(user_id, int(credits))
            logger.info("Added %d credits to user %s (session %s)", int(credits), user_id, session["id"])
        else:
            logger.warning("Skipping session %s: payment_status=%s metadata=%s", session["id"], session["payment_status"], metadata)

    return {"received": True}


def _add_credits(user_id: str, credits: int) -> None:
    """
    Calls the add_credits Postgres function in Supabase.

    Required SQL (run once in Supabase):
        CREATE OR REPLACE FUNCTION add_credits(p_user_id UUID, p_amount INTEGER)
        RETURNS INTEGER LANGUAGE plpgsql AS $$
        DECLARE new_balance INTEGER;
        BEGIN
          UPDATE users SET credits = credits + p_amount
          WHERE id = p_user_id RETURNING credits INTO new_balance;
          RETURN new_balance;
        END; $$;
    """
    from auth.credits import _db
    _db().rpc("add_credits", {"p_user_id": user_id, "p_amount": credits}).execute()
