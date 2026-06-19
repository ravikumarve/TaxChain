"""
Payment Service - Handles subscription logic and plan validation
Supports Razorpay (India) and Lemon Squeezy (Global)
"""

import razorpay
from typing import Optional, Dict, Any, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.subscription import Subscription
from app.config import settings
import logging
import httpx
import hmac
import hashlib

logger = logging.getLogger(__name__)

# Plan configuration as per AGENTS.md
PLAN_LIMITS = {
    'free': {
        'wallets': 1,
        'chains': ['eth'],
        'tx_history_years': 1,
        'export_csv': False,
        'export_pdf': False,
        'export_itr': False,
        'price_monthly_inr': 0,
        'price_monthly_usd': 0,
    },
    'starter': {
        'wallets': 3,
        'chains': ['eth', 'bnb', 'polygon'],
        'tx_history_years': 3,
        'export_csv': True,
        'export_pdf': False,
        'export_itr': False,
        'price_monthly_inr': 749,  # ~$9
        'price_monthly_usd': 9,
    },
    'pro': {
        'wallets': 999,
        'chains': ['eth', 'bnb', 'polygon', 'sol'],
        'tx_history_years': 10,
        'export_csv': True,
        'export_pdf': True,
        'export_itr': True,  # India ITR VDA — PRO ONLY
        'price_monthly_inr': 1599,  # ~$19
        'price_monthly_usd': 19,
    }
}


class PaymentService:
    """Service for handling payment operations and plan management"""
    
    def __init__(self):
        # Initialize Razorpay client
        self.razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        # Webhook idempotency: track processed event IDs to prevent duplicate processing
        self._processed_webhook_events: Set[str] = set()
        
    def get_plan_limits(self, plan: str) -> Dict[str, Any]:
        """Get limits and features for a given plan"""
        return PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    
    def check_plan_access(self, user: User, feature: str) -> bool:
        """Check if user's plan allows access to a specific feature"""
        plan_limits = self.get_plan_limits(user.plan)
        return plan_limits.get(feature, False)
    
    def check_wallet_limit(self, user: User, current_wallet_count: int) -> bool:
        """Check if user can add more wallets"""
        plan_limits = self.get_plan_limits(user.plan)
        return current_wallet_count < plan_limits['wallets']
    
    def check_chain_access(self, user: User, chain: str) -> bool:
        """Check if user's plan supports a specific blockchain"""
        plan_limits = self.get_plan_limits(user.plan)
        return chain in plan_limits['chains']
    
    def _get_razorpay_plan_id(self, plan: str) -> str:
        """Get Razorpay plan ID from settings based on plan name."""
        mapping = {
            'starter': settings.RAZORPAY_PLAN_STARTER,
            'pro': settings.RAZORPAY_PLAN_PRO,
        }
        return mapping.get(plan, '')

    def _get_lemonsqueezy_variant_id(self, plan: str) -> str:
        """Get Lemon Squeezy variant ID from settings based on plan name."""
        mapping = {
            'starter': settings.LEMONSQUEEZY_VARIANT_STARTER,
            'pro': settings.LEMONSQUEEZY_VARIANT_PRO,
        }
        return mapping.get(plan, '')

    def create_razorpay_order(self, user_id: str, plan: str) -> Dict[str, Any]:
        """
        Create a Razorpay order for subscription
        
        Args:
            user_id: User ID
            plan: Plan type (starter or pro)
            
        Returns:
            Razorpay order details
        """
        try:
            plan_limits = self.get_plan_limits(plan)
            amount = plan_limits['price_monthly_inr'] * 100  # Razorpay expects amount in paise
            
            order_data = {
                'amount': amount,
                'currency': 'INR',
                'receipt': f'receipt_{user_id}_{int(datetime.now().timestamp())}',
                'notes': {
                    'user_id': user_id,
                    'plan': plan
                }
            }
            
            order = self.razorpay_client.order.create(order_data)
            
            logger.info(f"Created Razorpay order {order['id']} for user {user_id}, plan {plan}")
            
            return {
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key_id': settings.RAZORPAY_KEY_ID,
                'plan': plan,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {str(e)}")
            raise
    
    def create_lemonsqueezy_checkout(self, user_id: str, plan: str) -> Dict[str, Any]:
        """
        Create a Lemon Squeezy checkout URL for subscription
        
        Args:
            user_id: User ID
            plan: Plan type (starter or pro)
            
        Returns:
            Lemon Squeezy checkout URL
        """
        try:
            variant_id = self._get_lemonsqueezy_variant_id(plan)
            if not variant_id:
                raise ValueError(f"Invalid plan: {plan}")
            
            # Create checkout session via Lemon Squeezy API
            headers = {
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {settings.LEMONSQUEEZY_API_KEY}'
            }
            
            checkout_data = {
                'data': {
                    'type': 'checkouts',
                    'attributes': {
                        'checkout_data': {
                            'custom': {
                                'user_id': user_id,
                                'plan': plan
                            }
                        }
                    },
                    'relationships': {
                        'store': {
                            'data': {
                                'type': 'stores',
                                'id': settings.LEMONSQUEEZY_STORE_ID
                            }
                        },
                        'variant': {
                            'data': {
                                'type': 'variants',
                                'id': variant_id
                            }
                        }
                    }
                }
            }
            
            # TODO: Make actual Lemon Squeezy API call when credentials are configured
            # async with httpx.AsyncClient() as client:
            #     resp = await client.post(
            #         'https://api.lemonsqueezy.com/v1/checkouts',
            #         headers=headers,
            #         json=checkout_data
            #     )
            #     resp.raise_for_status()
            #     result = resp.json()
            #     return {
            #         'checkout_url': result['data']['attributes']['url'],
            #         'variant_id': variant_id,
            #         'plan': plan,
            #         'user_id': user_id
            #     }
            
            logger.info(f"Would create Lemon Squeezy checkout for user {user_id}, plan {plan}")
            
            return {
                'checkout_url': f'https://lemonsqueezy.com/checkout/buy/{variant_id}',
                'variant_id': variant_id,
                'plan': plan,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Failed to create Lemon Squeezy checkout: {str(e)}")
            raise
    
    def is_event_processed(self, event_id: str) -> bool:
        """
        Check if a webhook event was already processed (idempotency).
        
        Args:
            event_id: Unique webhook event ID
            
        Returns:
            True if already processed
        """
        if event_id in self._processed_webhook_events:
            logger.warning(f"Duplicate webhook event detected: {event_id}")
            return True
        self._processed_webhook_events.add(event_id)
        return False

    def verify_razorpay_webhook(self, payload: bytes, signature: str) -> bool:
        """
        Verify Razorpay webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Razorpay signature from headers
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Failed to verify Razorpay webhook: {str(e)}")
            return False
    
    def verify_lemonsqueezy_webhook(self, payload: bytes, signature: str) -> bool:
        """
        Verify Lemon Squeezy webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Lemon Squeezy signature from headers
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = hmac.new(
                settings.LEMONSQUEEZY_WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Failed to verify Lemon Squeezy webhook: {str(e)}")
            return False
    
    def process_razorpay_payment(
        self, db: Session, payment_data: Dict[str, Any], event_id: Optional[str] = None
    ) -> Optional[Subscription]:
        """
        Process successful Razorpay payment and create/update subscription
        
        Args:
            db: Database session
            payment_data: Payment details from Razorpay webhook
            event_id: Unique webhook event ID for idempotency
            
        Returns:
            Created or updated subscription, or None if duplicate
        """
        try:
            # Idempotency check
            if event_id and self.is_event_processed(event_id):
                return None

            # Extract user_id and plan from payment notes
            user_id = payment_data.get('notes', {}).get('user_id')
            plan = payment_data.get('notes', {}).get('plan')
            
            if not user_id or not plan:
                raise ValueError("Missing user_id or plan in payment data")
            
            # Calculate subscription end date (1 month from now)
            current_period_end = datetime.now() + timedelta(days=30)
            
            # Check if user already has an active subscription
            existing_sub = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.provider == 'razorpay',
                Subscription.status == 'active'
            ).first()
            
            if existing_sub:
                # Update existing subscription
                existing_sub.plan = plan
                existing_sub.provider_sub_id = payment_data.get('order_id')
                existing_sub.current_period_end = current_period_end
                existing_sub.status = 'active'
                
                logger.info(f"Updated subscription {existing_sub.id} for user {user_id}")
            else:
                # Create new subscription
                subscription = Subscription(
                    user_id=user_id,
                    provider='razorpay',
                    provider_sub_id=payment_data.get('order_id'),
                    plan=plan,
                    status='active',
                    current_period_end=current_period_end
                )
                
                db.add(subscription)
                logger.info(f"Created new subscription for user {user_id}")
            
            # Update user's plan
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.plan = plan
            
            db.commit()
            db.refresh(subscription)
            
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to process Razorpay payment: {str(e)}")
            db.rollback()
            raise
    
    def process_lemonsqueezy_payment(
        self, db: Session, webhook_data: Dict[str, Any], event_id: Optional[str] = None
    ) -> Optional[Subscription]:
        """
        Process successful Lemon Squeezy payment and create/update subscription
        
        Args:
            db: Database session
            webhook_data: Webhook data from Lemon Squeezy
            
        Returns:
            Created or updated subscription
        """
        try:
            # Idempotency check
            event_id = webhook_data.get('data', {}).get('id')
            if event_id and self.is_event_processed(event_id):
                return None

            # Extract subscription details from webhook
            attributes = webhook_data.get('data', {}).get('attributes', {})
            custom_data = attributes.get('first_order_item', {}).get('custom_data', {})
            
            user_id = custom_data.get('user_id')
            plan = custom_data.get('plan')
            variant_id = attributes.get('first_order_item', {}).get('variant_id')
            
            if not user_id or not plan:
                raise ValueError("Missing user_id or plan in webhook data")
            
            # Map variant to plan
            starter_variant = self._get_lemonsqueezy_variant_id('starter')
            pro_variant = self._get_lemonsqueezy_variant_id('pro')
            if variant_id == starter_variant:
                plan = 'starter'
            elif variant_id == pro_variant:
                plan = 'pro'
            
            # Calculate subscription end date from renewal date
            renews_at = attributes.get('renews_at')
            if renews_at:
                current_period_end = datetime.fromisoformat(renews_at.replace('Z', '+00:00'))
            else:
                current_period_end = datetime.now() + timedelta(days=30)
            
            # Check if user already has an active subscription
            existing_sub = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.provider == 'lemonsqueezy',
                Subscription.status == 'active'
            ).first()
            
            if existing_sub:
                # Update existing subscription
                existing_sub.plan = plan
                existing_sub.provider_sub_id = webhook_data.get('data', {}).get('id')
                existing_sub.current_period_end = current_period_end
                existing_sub.status = 'active'
                
                logger.info(f"Updated subscription {existing_sub.id} for user {user_id}")
            else:
                # Create new subscription
                subscription = Subscription(
                    user_id=user_id,
                    provider='lemonsqueezy',
                    provider_sub_id=webhook_data.get('data', {}).get('id'),
                    plan=plan,
                    status='active',
                    current_period_end=current_period_end
                )
                
                db.add(subscription)
                logger.info(f"Created new subscription for user {user_id}")
            
            # Update user's plan
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.plan = plan
            
            db.commit()
            db.refresh(subscription)
            
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to process Lemon Squeezy payment: {str(e)}")
            db.rollback()
            raise
    
    def cancel_subscription(self, db: Session, user_id: str) -> bool:
        """
        Cancel user's active subscription
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if cancellation was successful
        """
        try:
            subscription = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == 'active'
            ).first()
            
            if not subscription:
                logger.warning(f"No active subscription found for user {user_id}")
                return False
            
            # Update subscription status
            subscription.status = 'cancelled'
            
            # Note: We don't downgrade the user's plan immediately
            # They keep their plan until the period ends
            
            db.commit()
            logger.info(f"Cancelled subscription {subscription.id} for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            db.rollback()
            return False
    
    def check_subscription_status(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Check user's subscription status and plan details
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Subscription status and plan details
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'status': 'error', 'message': 'User not found'}
            
            subscription = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == 'active'
            ).first()
            
            plan_limits = self.get_plan_limits(user.plan)
            
            return {
                'status': 'success',
                'plan': user.plan,
                'is_active': subscription is not None,
                'provider': subscription.provider if subscription else None,
                'current_period_end': subscription.current_period_end.isoformat() if subscription else None,
                'limits': plan_limits
            }
            
        except Exception as e:
            logger.error(f"Failed to check subscription status: {str(e)}")
            return {'status': 'error', 'message': str(e)}


# Global payment service instance
payment_service = PaymentService()