# 🚀 Deploy ScrapeMaster to Railway in 5 Minutes

## Prerequisites
1. Create accounts at:
   - [Railway.app](https://railway.app) (for hosting)
   - [ScraperAPI.com](https://www.scraperapi.com) (get API key)
   - [Stripe.com](https://stripe.com) (for payments)

## Step 1: Fork & Clone
```bash
git clone https://github.com/your-username/scrapemaster-intelligence.git
cd scrapemaster-intelligence
```

## Step 2: Install Railway CLI
```bash
# Windows (PowerShell)
iwr -useb https://railway.app/install.ps1 | iex

# Mac/Linux
curl -fsSL https://railway.app/install.sh | sh
```

## Step 3: Deploy to Railway
```bash
# Login to Railway
railway login

# Create new project
railway init

# Deploy
railway up
```

## Step 4: Set Environment Variables
In Railway dashboard, add these variables:

```
SCRAPERAPI_KEY=your_scraperapi_key_here
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
APP_SECRET_KEY=generate_random_secret_here
ADMIN_EMAIL=your-email@example.com
```

## Step 5: Get Your URL
Railway will give you a URL like: `scrapemaster.up.railway.app`

## Step 6: Create Stripe Payment Links
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/payment-links)
2. Create payment links for each plan:
   - Starter: $99/month
   - Professional: $199/month
   - Enterprise: $499/month
3. Update the links in `src/landing_page.py`

## Step 7: Launch!
Your app is now live! Start marketing:
1. Share your Railway URL
2. Post in relevant communities
3. Reach out to potential customers

## Quick Commands
```bash
# View logs
railway logs

# Open dashboard
railway open

# Redeploy after changes
railway up
```

## Need Help?
- Railway Docs: https://docs.railway.app
- Email: support@scrapemaster.ai 