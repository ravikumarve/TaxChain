# TaxChain Testing Guide

This guide covers testing the payment flow and plan restrictions for TaxChain.

## Prerequisites

- Backend running locally or deployed
- Frontend running locally or deployed
- Test accounts for Razorpay and Lemon Squeezy
- PostgreSQL database with test data

## Test Environment Setup

### Local Testing

1. Start the backend:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Ensure environment variables are set in `.env` files

### Production Testing

Use your deployed URLs:
- Backend: `https://taxchain-backend.onrender.com`
- Frontend: `https://taxchain.vercel.app`

## Test Cases

### 1. User Registration and Login

**Test Steps:**
1. Visit `/auth/signup`
2. Fill in registration form
3. Submit and verify account creation
4. Login with new credentials
5. Verify JWT token is stored in localStorage

**Expected Results:**
- User is created in database
- JWT token is returned and stored
- User is redirected to dashboard
- Default plan is 'free'

### 2. Plan Limits Verification

**Test Steps:**
1. Login as free user
2. Try to add more than 1 wallet
3. Try to add BNB chain wallet
4. Try to export CSV
5. Try to export PDF
6. Try to export ITR

**Expected Results:**
- Wallet limit enforced (max 1 for free)
- Chain access enforced (ETH only for free)
- Export features blocked for free plan
- Appropriate error messages shown

### 3. Plan Upgrade Flow (Razorpay)

**Test Steps:**
1. Login as free user
2. Click "Upgrade" button in sidebar
3. Select "Starter" plan
4. Complete Razorpay payment (test mode)
5. Verify payment success
6. Check plan is updated to 'starter'
7. Verify new features are unlocked

**Expected Results:**
- Razorpay checkout opens
- Payment is processed successfully
- User plan is updated in database
- New features (CSV export, 3 wallets) are available
- Plan badge shows "Starter"

### 4. Plan Upgrade Flow (Lemon Squeezy)

**Test Steps:**
1. Login as free user
2. Visit `/pricing` page
3. Click "Upgrade to Pro" for Lemon Squeezy
4. Complete Lemon Squeezy checkout (test mode)
5. Verify payment success
6. Check plan is updated to 'pro'
7. Verify all features are unlocked

**Expected Results:**
- Redirected to Lemon Squeezy checkout
- Payment is processed successfully
- User plan is updated in database
- All features (PDF, ITR export) are available
- Plan badge shows "Pro"

### 5. Webhook Verification

**Test Steps:**
1. Trigger a test payment in Razorpay/Lemon Squeezy dashboard
2. Send test webhook to backend endpoint
3. Verify webhook signature is validated
4. Check subscription is created/updated in database
5. Verify user plan is updated

**Expected Results:**
- Webhook signature is verified
- Subscription record is created/updated
- User plan is updated
- Appropriate logging occurs

### 6. Plan Downgrade/Cancel

**Test Steps:**
1. Login as paid user
2. Click "Cancel Subscription" button
3. Confirm cancellation
4. Verify subscription status is 'cancelled'
5. Verify plan remains active until period end
6. Check features still work during grace period

**Expected Results:**
- Subscription status is updated to 'cancelled'
- User plan is not immediately downgraded
- Features continue to work until period end
- Appropriate confirmation message shown

### 7. Feature Gates Testing

**Test Steps for Each Plan:**

**Free Plan:**
- [ ] Can add 1 wallet max
- [ ] Can only use ETH chain
- [ ] Cannot export CSV
- [ ] Cannot export PDF
- [ ] Cannot export ITR
- [ ] Can view current year data only

**Starter Plan:**
- [ ] Can add 3 wallets max
- [ ] Can use ETH, BNB, Polygon chains
- [ ] Can export CSV
- [ ] Cannot export PDF
- [ ] Cannot export ITR
- [ ] Can view 3 years of data

**Pro Plan:**
- [ ] Can add unlimited wallets
- [ ] Can use all chains including Solana
- [ ] Can export CSV
- [ ] Can export PDF
- [ ] Can export ITR
- [ ] Can view 10 years of data

### 8. Pricing Page Testing

**Test Steps:**
1. Visit `/pricing` page
2. Verify all 3 plans are displayed
3. Check pricing is correct (INR/USD)
4. Verify features are listed correctly
5. Test upgrade buttons for each plan
6. Verify FAQ section is displayed
7. Test responsive design on mobile

**Expected Results:**
- All plans displayed correctly
- Pricing matches configuration
- Features are accurate
- Upgrade buttons work
- FAQ is readable
- Mobile layout is responsive

### 9. Landing Page Testing

**Test Steps:**
1. Visit landing page (`/`)
2. Verify hero section is displayed
3. Check features section
4. Verify pricing preview
5. Test FAQ section
6. Verify CTA buttons work
7. Test navigation links
8. Check responsive design

**Expected Results:**
- All sections displayed correctly
- Navigation works
- CTA buttons redirect to signup/pricing
- Mobile layout is responsive
- Loading performance is good

### 10. Error Handling Testing

**Test Scenarios:**
1. Invalid wallet address format
2. Network timeout during wallet sync
3. Payment failure
4. Webhook signature mismatch
5. Invalid JWT token
6. Database connection failure
7. Rate limit exceeded

**Expected Results:**
- Appropriate error messages
- Graceful degradation
- User-friendly error UI
- Proper error logging
- No sensitive data leaked

## Automated Testing

### Backend Tests

Run the existing test suite:

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### End-to-End Tests

```bash
npm run test:e2e
```

## Performance Testing

### Load Testing

Use tools like Apache Bench or k6:

```bash
# Test API endpoints
ab -n 1000 -c 10 https://taxchain-backend.onrender.com/api/health

# Test frontend
ab -n 1000 -c 10 https://taxchain.vercel.app/
```

### Database Performance

Monitor query times and connection pooling:

```sql
-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

## Security Testing

### API Security

- [ ] SQL injection attempts
- [ ] XSS attempts
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Input validation
- [ ] Authentication bypass attempts

### Payment Security

- [ ] Webhook signature verification
- [ ] Payment amount validation
- [ ] Plan validation
- [ ] Replay attack prevention

## Browser Compatibility

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

## Accessibility Testing

- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Color contrast ratios
- [ ] Alt text for images
- [ ] ARIA labels

## Test Data Cleanup

After testing, clean up test data:

```sql
-- Delete test users
DELETE FROM users WHERE email LIKE '%test%';

-- Delete test subscriptions
DELETE FROM subscriptions WHERE user_id IN (
    SELECT id FROM users WHERE email LIKE '%test%'
);

-- Delete test wallets
DELETE FROM wallets WHERE user_id IN (
    SELECT id FROM users WHERE email LIKE '%test%'
);
```

## Continuous Integration

Set up GitHub Actions for automated testing:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/
      - name: Run frontend tests
        run: |
          cd frontend
          npm install
          npm test
```

## Test Reporting

Document test results in:

1. Test execution summary
2. Pass/fail rates
3. Performance metrics
4. Security findings
5. Browser compatibility issues
6. Accessibility audit results

## Sign-off Criteria

Before going live, ensure:

- [ ] All critical tests pass
- [ ] No security vulnerabilities
- [ ] Performance meets requirements
- [ ] Payment flow works end-to-end
- [ ] Webhooks are verified
- [ ] Error handling is robust
- [ ] Documentation is complete
- [ ] Monitoring is configured

## Troubleshooting

### Payment Flow Issues

**Problem**: Razorpay checkout doesn't open
- Check: API key is correct
- Check: Order creation succeeded
- Check: Razorpay script is loaded

**Problem**: Webhook not received
- Check: Webhook URL is accessible
- Check: Firewall allows incoming requests
- Check: Signature verification logic

### Plan Gates Issues

**Problem**: Features not unlocking after upgrade
- Check: Database was updated
- Check: Frontend refreshed plan data
- Check: JWT token includes plan info

**Problem**: Limits not enforced
- Check: Backend validation logic
- Check: Plan limits configuration
- Check: User plan in database

## Next Steps

After successful testing:

1. Deploy to production
2. Monitor error logs
3. Set up alerts
4. Create user documentation
5. Plan for scaling