# TaxChain Deployment Guide

This guide will help you deploy TaxChain to production using Vercel (frontend), Render (backend), and Supabase (database).

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL database (we recommend Supabase)
- Razorpay account (for Indian payments)
- Lemon Squeezy account (for global payments)
- Etherscan, BscScan, PolygonScan API keys

## Architecture

```
┌─────────────────┐
│   Vercel        │ ← Frontend (Next.js)
│   Frontend      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Render        │ ← Backend (FastAPI)
│   Backend       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Supabase      │ ← Database (PostgreSQL)
│   PostgreSQL    │
└─────────────────┘
```

## Step 1: Set Up Supabase Database

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Go to Settings → Database
3. Copy the connection string (URI format)
4. Run the database migrations:

```bash
cd backend
alembic upgrade head
```

## Step 2: Deploy Backend to Render

1. Create a new account at [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure the service:

   - **Name**: taxchain-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Branch**: `main`

5. Add environment variables in Render dashboard:

   ```
   DATABASE_URL=your-supabase-connection-string
   SECRET_KEY=your-jwt-secret-key
   FRONTEND_URL=https://your-vercel-app.vercel.app
   ETHERSCAN_API_KEY=your-etherscan-key
   BSCSCAN_API_KEY=your-bscscan-key
   POLYGONSCAN_API_KEY=your-polygonscan-key
   SOLSCAN_API_KEY=your-solscan-key
   RAZORPAY_KEY_ID=your-razorpay-key-id
   RAZORPAY_KEY_SECRET=your-razorpay-key-secret
   LEMONSQUEEZY_API_KEY=your-lemonsqueezy-api-key
   LEMONSQUEEZY_WEBHOOK_SECRET=your-lemonsqueezy-webhook-secret
   ```

6. Deploy the service
7. Copy the Render service URL (e.g., `https://taxchain-backend.onrender.com`)

## Step 3: Deploy Frontend to Vercel

1. Create a new account at [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Configure the project:

   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

4. Add environment variables in Vercel dashboard:

   ```
   NEXT_PUBLIC_API_URL=https://taxchain-backend.onrender.com
   NEXT_PUBLIC_RAZORPAY_KEY_ID=your-razorpay-key-id
   ```

5. Deploy the project
6. Copy the Vercel URL (e.g., `https://taxchain.vercel.app`)

## Step 4: Configure Payment Providers

### Razorpay (India)

1. Create a Razorpay account at [razorpay.com](https://razorpay.com)
2. Go to Settings → API Keys
3. Copy the Key ID and Key Secret
4. Create subscription plans in Razorpay Dashboard:
   - Starter Plan: ₹749/month
   - Pro Plan: ₹1,599/month
5. Update the plan IDs in `backend/app/services/payment_service.py`:

   ```python
   RAZORPAY_PLAN_IDS = {
       'starter': 'plan_YOUR_STARTER_PLAN_ID',
       'pro': 'plan_YOUR_PRO_PLAN_ID'
   }
   ```

6. Set up webhooks:
   - Go to Settings → Webhooks
   - Add webhook URL: `https://taxchain-backend.onrender.com/api/webhooks/razorpay`
   - Select events: `payment.captured`, `subscription.cancelled`

### Lemon Squeezy (Global)

1. Create a Lemon Squeezy account at [lemonsqueezy.com](https://lemonsqueezy.com)
2. Create products and variants:
   - Starter Plan: $9/month
   - Pro Plan: $19/month
3. Copy the API key and webhook secret
4. Update the product IDs in `backend/app/services/payment_service.py`:

   ```python
   LEMONSQUEEZY_PRODUCT_IDS = {
       'starter': 'YOUR_STARTER_VARIANT_ID',
       'pro': 'YOUR_PRO_VARIANT_ID'
   }
   ```

5. Set up webhooks:
   - Go to Settings → Webhooks
   - Add webhook URL: `https://taxchain-backend.onrender.com/api/webhooks/lemonsqueezy`
   - Select events: `order_created`, `subscription_created`, `subscription_updated`, `subscription_cancelled`

## Step 5: Update CORS Configuration

Update the `FRONTEND_URL` in your backend environment variables to match your Vercel URL.

## Step 6: Test the Deployment

1. Visit your Vercel URL
2. Test user registration and login
3. Test wallet connection
4. Test payment flow (use test mode for Razorpay/Lemon Squeezy)
5. Verify webhooks are working
6. Test plan upgrades and feature gates

## Step 7: Monitor and Scale

### Monitoring

- **Render**: View logs and metrics in Render dashboard
- **Vercel**: View analytics and logs in Vercel dashboard
- **Supabase**: Monitor database performance in Supabase dashboard

### Scaling

- **Backend**: Render automatically scales based on traffic
- **Frontend**: Vercel handles global CDN automatically
- **Database**: Upgrade Supabase plan as needed

## Security Checklist

- [ ] All API keys are in environment variables (not in code)
- [ ] CORS is configured for production domain only
- [ ] JWT secret is strong (32+ characters)
- [ ] Database connection uses SSL
- [ ] Webhook signatures are verified
- [ ] Rate limiting is enabled
- [ ] HTTPS is enforced

## Troubleshooting

### Backend won't start

- Check Render logs for errors
- Verify all environment variables are set
- Ensure database migrations ran successfully

### Frontend can't connect to backend

- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS configuration
- Ensure backend is running and accessible

### Payments not working

- Verify API keys are correct
- Check webhook URLs are accessible
- Test in sandbox/test mode first
- Check payment provider logs

### Database connection issues

- Verify `DATABASE_URL` is correct
- Ensure Supabase project is active
- Check connection pooling settings

## Cost Estimates

### Free Tier (Launch)

- **Vercel**: Free (100GB bandwidth, unlimited builds)
- **Render**: Free (750 hours/month, 512MB RAM)
- **Supabase**: Free (500MB database, 1GB file storage)

### Paid Tier (Growth)

- **Vercel**: $20/month (Pro plan)
- **Render**: $7/month (Starter plan)
- **Supabase**: $25/month (Pro plan)

**Total**: ~$52/month for production-grade infrastructure

## Next Steps

1. Set up error monitoring (Sentry free tier)
2. Configure email notifications for important events
3. Set up automated backups
4. Create analytics tracking
5. Implement A/B testing for pricing page

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/yourusername/taxchain/issues)
- Email: support@taxchain.com
- Documentation: [docs.taxchain.com](https://docs.taxchain.com)