# 🚀 Deploy ScrapeMaster to Railway - Quick Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Name it: `scrapemaster-intelligence`
3. Make it **Private** (for now)
4. Click "Create repository"

## Step 2: Push Your Code to GitHub

Open a **new PowerShell window** (to refresh PATH) and run:

```bash
cd C:\ScrapeMaster-Intelligence

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial ScrapeMaster deployment"

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/scrapemaster-intelligence.git

# Push to GitHub
git push -u origin main
```

If you get an error about 'main' branch, try:
```bash
git branch -M main
git push -u origin main
```

## Step 3: Connect to Railway

1. Go to your Railway project: https://railway.com/project/81eab581-7f70-40f3-8503-5b4810df55e0
2. Click on your service "elegant-wonder"
3. Go to **Settings** tab
4. Under **Deploy**, click **Connect GitHub repo**
5. Select your `scrapemaster-intelligence` repository
6. Railway will automatically deploy!

## Step 4: Set Your Domain

1. In Railway, go to **Settings** → **Networking**
2. Click **Generate Domain**
3. Your app will be live at something like: `scrapemaster-abc123.up.railway.app`

## Step 5: Add Real API Keys

Replace the placeholder environment variables with real ones:

1. **ScraperAPI**: Sign up at https://www.scraperapi.com (free trial)
2. **Stripe**: Get test keys from https://dashboard.stripe.com/test/apikeys

In Railway dashboard:
- Click on Variables tab
- Update each variable with real values

## 🎯 What's Next?

1. Visit your live app URL
2. Start marketing immediately (use templates in `marketing/outreach_templates.md`)
3. Get your first 3 customers today!

## 💡 Pro Tips

- Use the landing page first to collect leads
- Switch to the main app once you have paying customers
- Focus on Amazon FBA sellers - they need this most! 