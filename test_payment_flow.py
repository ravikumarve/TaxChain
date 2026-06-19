#!/usr/bin/env python3
"""
Test script for payment flow
Run this to verify the payment integration is working correctly
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your backend URL
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "Test123456"


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"     {details}")


def register_user() -> Dict[str, Any]:
    """Register a test user"""
    print_section("1. User Registration")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if response.status_code == 200:
            print_result("User Registration", True, f"User ID: {result.get('id')}")
            return result
        else:
            print_result("User Registration", False, result.get('detail', 'Unknown error'))
            return None
    except Exception as e:
        print_result("User Registration", False, str(e))
        return None


def login_user() -> Dict[str, Any]:
    """Login and get access token"""
    print_section("2. User Login")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if response.status_code == 200:
            token = result.get('access_token')
            print_result("User Login", True, f"Token received: {token[:20]}...")
            return {"token": token, "user": result.get('user')}
        else:
            print_result("User Login", False, result.get('detail', 'Unknown error'))
            return None
    except Exception as e:
        print_result("User Login", False, str(e))
        return None


def get_subscription_status(token: str) -> Dict[str, Any]:
    """Get subscription status"""
    print_section("3. Subscription Status")
    
    url = f"{BASE_URL}/api/payments/subscription-status"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print_result("Get Subscription Status", True, f"Plan: {result.get('plan')}")
            return result
        else:
            print_result("Get Subscription Status", False, result.get('detail', 'Unknown error'))
            return None
    except Exception as e:
        print_result("Get Subscription Status", False, str(e))
        return None


def get_plan_limits(plan: str) -> Dict[str, Any]:
    """Get plan limits"""
    print_section("4. Plan Limits")
    
    url = f"{BASE_URL}/api/payments/plan-limits/{plan}"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if response.status_code == 200:
            limits = result.get('limits', {})
            print_result(f"Get {plan.upper()} Plan Limits", True, 
                        f"Wallets: {limits.get('wallets')}, Chains: {len(limits.get('chains', []))}")
            return result
        else:
            print_result(f"Get {plan.upper()} Plan Limits", False, result.get('detail', 'Unknown error'))
            return None
    except Exception as e:
        print_result(f"Get {plan.upper()} Plan Limits", False, str(e))
        return None


def create_payment_order(token: str, plan: str, provider: str) -> Dict[str, Any]:
    """Create a payment order"""
    print_section(f"5. Create Payment Order ({provider.upper()} - {plan.upper()})")
    
    url = f"{BASE_URL}/api/payments/create-order"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "plan": plan,
        "provider": provider
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            if provider == 'razorpay':
                print_result("Create Razorpay Order", True, 
                            f"Order ID: {result.get('order_id')}, Amount: {result.get('amount')}")
            else:
                print_result("Create Lemon Squeezy Checkout", True,
                            f"Checkout URL: {result.get('checkout_url')}")
            return result
        else:
            print_result("Create Payment Order", False, result.get('detail', 'Unknown error'))
            return None
    except Exception as e:
        print_result("Create Payment Order", False, str(e))
        return None


def get_pricing() -> Dict[str, Any]:
    """Get pricing information"""
    print_section("6. Pricing Information")
    
    url = f"{BASE_URL}/api/payments/pricing"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if response.status_code == 200:
            plans = result.get('plans', {})
            print_result("Get Pricing", True, f"Available plans: {list(plans.keys())}")
            
            # Print pricing details
            for plan_name, plan_data in plans.items():
                print(f"\n  {plan_name.upper()}:")
                print(f"    Price (INR): ₹{plan_data.get('price_monthly_inr')}")
                print(f"    Price (USD): ${plan_data.get('price_monthly_usd')}")
                print(f"    Wallets: {plan_data.get('wallets')}")
                print(f"    Chains: {', '.join(plan_data.get('chains', []))}")
            
            return result
        else:
            print_result("Get Pricing", False, result.get('detail', 'Unknown error'))
            return None
    except Exception as e:
        print_result("Get Pricing", False, str(e))
        return None


def test_plan_gates(token: str) -> bool:
    """Test plan feature gates"""
    print_section("7. Plan Feature Gates")
    
    # Test different plan features
    tests = [
        ("Free Plan - CSV Export", "free", "export_csv", False),
        ("Free Plan - PDF Export", "free", "export_pdf", False),
        ("Free Plan - ITR Export", "free", "export_itr", False),
        ("Starter Plan - CSV Export", "starter", "export_csv", True),
        ("Starter Plan - PDF Export", "starter", "export_pdf", False),
        ("Pro Plan - CSV Export", "pro", "export_csv", True),
        ("Pro Plan - PDF Export", "pro", "export_pdf", True),
        ("Pro Plan - ITR Export", "pro", "export_itr", True),
    ]
    
    all_passed = True
    
    for test_name, plan, feature, expected in tests:
        url = f"{BASE_URL}/api/payments/plan-limits/{plan}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                result = response.json()
                limits = result.get('limits', {})
                actual = limits.get(feature, False)
                passed = actual == expected
                print_result(test_name, passed, f"Expected: {expected}, Got: {actual}")
                if not passed:
                    all_passed = False
            else:
                print_result(test_name, False, "Failed to get plan limits")
                all_passed = False
        except Exception as e:
            print_result(test_name, False, str(e))
            all_passed = False
    
    return all_passed


def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("  TaxChain Payment Flow Test Suite")
    print("="*60)
    
    # Test sequence
    results = []
    
    # 1. Register user
    user = register_user()
    results.append(user is not None)
    
    # 2. Login
    auth_data = login_user()
    results.append(auth_data is not None)
    
    if not auth_data:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    token = auth_data['token']
    
    # 3. Get subscription status
    sub_status = get_subscription_status(token)
    results.append(sub_status is not None)
    
    # 4. Get plan limits for all plans
    for plan in ['free', 'starter', 'pro']:
        limits = get_plan_limits(plan)
        results.append(limits is not None)
    
    # 5. Get pricing
    pricing = get_pricing()
    results.append(pricing is not None)
    
    # 6. Create payment orders (test mode)
    # Note: These will fail without actual API keys, but we test the endpoint
    razorpay_order = create_payment_order(token, 'starter', 'razorpay')
    results.append(razorpay_order is not None or 'API key' in str(razorpay_order))
    
    lemonsqueezy_checkout = create_payment_order(token, 'pro', 'lemonsqueezy')
    results.append(lemonsqueezy_checkout is not None or 'API key' in str(lemonsqueezy_checkout))
    
    # 7. Test plan gates
    gates_passed = test_plan_gates(token)
    results.append(gates_passed)
    
    # Summary
    print_section("Test Summary")
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()