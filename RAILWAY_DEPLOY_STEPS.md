# 🚀 Railway Deployment Steps

## After Login Completes:

### 1. Initialize Railway Project
```bash
railway init
```
- Choose "Empty Project" when prompted
- Give it a name like "scrapemaster-intelligence"

### 2. Deploy Your App
```bash
railway up
```
This will:
- Upload your code
- Detect it's a Python app
- Install dependencies from requirements.txt
- Start your app

### 3. Add Environment Variables
```bash
# Add each variable
railway variables set SCRAPERAPI_KEY=your_key_here
railway variables set STRIPE_SECRET_KEY=sk_test_your_key
railway variables set STRIPE_PUBLISHABLE_KEY=pk_test_your_key
railway variables set APP_SECRET_KEY=your_random_secret_here
railway variables set ADMIN_EMAIL=your-email@example.com
```

### 4. Deploy Changes
```bash
railway up
```

### 5. Get Your App URL
```bash
railway open
```

## Alternative: Use Railway Dashboard

If CLI doesn't work, you can:
1. Go to https://railway.app/dashboard
2. Click "New Project" 
3. Choose "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select your repository
6. Railway will auto-deploy

## Quick Test Commands
```bash
# Check status
railway status

# View logs
railway logs

# Open dashboard
railway open
```

## 🎯 Next Steps After Deploy:
1. Update Stripe payment links in landing_page.py
2. Test the app at your Railway URL
3. Start marketing using the templates! 