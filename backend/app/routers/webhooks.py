"""
Webhooks Router - Handles payment confirmation webhooks
Supports Razorpay and Lemon Squeezy webhooks
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.services.payment_service import payment_service
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Razorpay payment webhooks
    
    Webhook events handled:
    - payment.captured: Successful payment
    - subscription.cancelled: Subscription cancelled
    """
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get('X-Razorpay-Signature')
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing signature"
            )
        
        # Verify webhook signature
        if not payment_service.verify_razorpay_webhook(payload, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        # Parse webhook data
        webhook_data = json.loads(payload)
        event_type = webhook_data.get('event')
        
        logger.info(f"Received Razorpay webhook: {event_type}")
        
        # Handle different event types
        if event_type == 'payment.captured':
            # Extract payment details
            payment_data = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
            
            # Process the payment
            subscription = payment_service.process_razorpay_payment(
                db=db,
                payment_data=payment_data
            )
            
            logger.info(f"Successfully processed Razorpay payment for subscription {subscription.id}")
            
            return {"status": "success", "subscription_id": str(subscription.id)}
        
        elif event_type == 'subscription.cancelled':
            # Handle subscription cancellation
            subscription_data = webhook_data.get('payload', {}).get('subscription', {}).get('entity', {})
            notes = subscription_data.get('notes', {})
            user_id = notes.get('user_id')
            
            if user_id:
                payment_service.cancel_subscription(db=db, user_id=user_id)
                logger.info(f"Cancelled subscription for user {user_id}")
            
            return {"status": "success", "message": "Subscription cancelled"}
        
        else:
            logger.warning(f"Unhandled Razorpay event: {event_type}")
            return {"status": "ignored", "message": "Event not handled"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process Razorpay webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@router.post("/lemonsqueezy")
async def lemonsqueezy_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Lemon Squeezy payment webhooks
    
    Webhook events handled:
    - order_created: New order created
    - subscription_created: New subscription created
    - subscription_updated: Subscription updated
    - subscription_cancelled: Subscription cancelled
    """
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get('X-Signature')
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing signature"
            )
        
        # Verify webhook signature
        if not payment_service.verify_lemonsqueezy_webhook(payload, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        # Parse webhook data
        webhook_data = json.loads(payload)
        meta = webhook_data.get('meta', {})
        event_name = meta.get('event_name')
        
        logger.info(f"Received Lemon Squeezy webhook: {event_name}")
        
        # Handle different event types
        if event_name in ['order_created', 'subscription_created', 'subscription_updated']:
            # Process the subscription
            subscription = payment_service.process_lemonsqueezy_payment(
                db=db,
                webhook_data=webhook_data
            )
            
            logger.info(f"Successfully processed Lemon Squeezy webhook for subscription {subscription.id}")
            
            return {"status": "success", "subscription_id": str(subscription.id)}
        
        elif event_name == 'subscription_cancelled':
            # Handle subscription cancellation
            attributes = webhook_data.get('data', {}).get('attributes', {})
            custom_data = attributes.get('first_order_item', {}).get('custom_data', {})
            user_id = custom_data.get('user_id')
            
            if user_id:
                payment_service.cancel_subscription(db=db, user_id=user_id)
                logger.info(f"Cancelled subscription for user {user_id}")
            
            return {"status": "success", "message": "Subscription cancelled"}
        
        else:
            logger.warning(f"Unhandled Lemon Squeezy event: {event_name}")
            return {"status": "ignored", "message": "Event not handled"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process Lemon Squeezy webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@router.get("/health")
async def webhook_health():
    """
    Health check endpoint for webhooks
    """
    return {
        "status": "healthy",
        "message": "Webhook endpoints are operational"
    }