"""
Payments Router - Handles payment creation and management
Supports Razorpay (India) and Lemon Squeezy (Global)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.payment_service import payment_service, PLAN_LIMITS
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class CreatePaymentRequest(BaseModel):
    plan: str  # 'starter' or 'pro'
    provider: str  # 'razorpay' or 'lemonsqueezy'


class PaymentResponse(BaseModel):
    status: str
    provider: str
    checkout_url: str = None
    order_id: str = None
    key_id: str = None
    amount: int = None
    currency: str = None
    plan: str


class PlanLimitsResponse(BaseModel):
    plan: str
    limits: Dict[str, Any]


class SubscriptionStatusResponse(BaseModel):
    status: str
    plan: str
    is_active: bool
    provider: str = None
    current_period_end: str = None
    limits: Dict[str, Any]


@router.post("/create-order", response_model=PaymentResponse)
async def create_payment_order(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment order for subscription upgrade
    
    - **plan**: 'starter' or 'pro'
    - **provider**: 'razorpay' (India) or 'lemonsqueezy' (Global)
    """
    try:
        # Validate plan
        if request.plan not in ['starter', 'pro']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan. Must be 'starter' or 'pro'"
            )
        
        # Validate provider
        if request.provider not in ['razorpay', 'lemonsqueezy']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid provider. Must be 'razorpay' or 'lemonsqueezy'"
            )
        
        # Check if user already has this plan or higher
        current_plan_limits = PLAN_LIMITS.get(current_user.plan, PLAN_LIMITS['free'])
        new_plan_limits = PLAN_LIMITS.get(request.plan, PLAN_LIMITS['free'])
        
        # Simple plan hierarchy: free < starter < pro
        plan_hierarchy = {'free': 0, 'starter': 1, 'pro': 2}
        if plan_hierarchy.get(current_user.plan, 0) >= plan_hierarchy.get(request.plan, 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have {current_user.plan} plan or higher"
            )
        
        # Create payment order based on provider
        if request.provider == 'razorpay':
            order_data = payment_service.create_razorpay_order(
                user_id=str(current_user.id),
                plan=request.plan
            )
            
            return PaymentResponse(
                status="success",
                provider="razorpay",
                order_id=order_data['order_id'],
                key_id=order_data['key_id'],
                amount=order_data['amount'],
                currency=order_data['currency'],
                plan=request.plan
            )
        
        else:  # lemonsqueezy
            checkout_data = payment_service.create_lemonsqueezy_checkout(
                user_id=str(current_user.id),
                plan=request.plan
            )
            
            return PaymentResponse(
                status="success",
                provider="lemonsqueezy",
                checkout_url=checkout_data['checkout_url'],
                plan=request.plan
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create payment order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment order"
        )


@router.get("/plan-limits/{plan}", response_model=PlanLimitsResponse)
async def get_plan_limits(plan: str):
    """
    Get limits and features for a specific plan
    
    - **plan**: 'free', 'starter', or 'pro'
    """
    try:
        if plan not in PLAN_LIMITS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        return PlanLimitsResponse(
            plan=plan,
            limits=PLAN_LIMITS[plan]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plan limits: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get plan limits"
        )


@router.get("/subscription-status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription status and plan details
    """
    try:
        status_data = payment_service.check_subscription_status(
            db=db,
            user_id=str(current_user.id)
        )
        
        if status_data['status'] == 'error':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=status_data['message']
            )
        
        return SubscriptionStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get subscription status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription status"
        )


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's active subscription
    Note: User keeps their plan until the current billing period ends
    """
    try:
        success = payment_service.cancel_subscription(
            db=db,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        return {
            "status": "success",
            "message": "Subscription cancelled successfully. Your plan remains active until the end of the current billing period."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.get("/pricing")
async def get_pricing():
    """
    Get pricing information for all plans
    """
    try:
        pricing_info = {}
        
        for plan_name, limits in PLAN_LIMITS.items():
            pricing_info[plan_name] = {
                'name': plan_name.capitalize(),
                'price_monthly_inr': limits.get('price_monthly_inr', 0),
                'price_monthly_usd': limits.get('price_monthly_usd', 0),
                'wallets': limits['wallets'],
                'chains': limits['chains'],
                'tx_history_years': limits['tx_history_years'],
                'export_csv': limits['export_csv'],
                'export_pdf': limits['export_pdf'],
                'export_itr': limits['export_itr'],
            }
        
        return {
            "status": "success",
            "plans": pricing_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get pricing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pricing"
        )