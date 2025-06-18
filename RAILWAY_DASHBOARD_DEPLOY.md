# 🚀 Deploy via Railway Dashboard (Easier Method)

Since you're already logged into Railway, let's deploy through the web dashboard:

## Step 1: Create New Project
1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**

## Step 2: Connect GitHub
1. Click **"Configure GitHub App"**
2. Authorize Railway to access your repositories
3. Select your ScrapeMaster repository (or create one first)

## Step 3: If You Don't Have a GitHub Repo Yet
```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial ScrapeMaster deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/scrapemaster-intelligence.git
git push -u origin main
```

## Step 4: Configure in Railway Dashboard
Once connected:

1. **Add Environment Variables** (click on your service → Variables):
   ```
   SCRAPERAPI_KEY=your_scraperapi_key_here
   STRIPE_SECRET_KEY=sk_test_your_stripe_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
   APP_SECRET_KEY=generate_a_random_secret_key_here
   ADMIN_EMAIL=your-email@example.com
   ```

2. **Settings Tab**:
   - Start Command: Leave empty (will use Procfile)
   - Build Command: Leave empty
   - Watch Paths: Leave default

3. Railway will automatically:
   - Detect Python app
   - Install requirements.txt
   - Use the Procfile to start

## Step 5: Get Your URL
1. Go to Settings tab
2. Under "Domains" click **"Generate Domain"**
3. Your app will be live at something like: `scrapemaster.up.railway.app`

## Alternative: Deploy Without GitHub
1. Install Railway CLI properly:
   ```bash
   # Try with winget
   winget install Railway.Railway
   
   # Or download directly:
   # Go to https://github.com/railwayapp/cli/releases
   # Download railway-v3.x.x-x86_64-pc-windows-msvc.exe
   # Rename to railway.exe and add to PATH
   ```

2. Then deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

## 🎯 Quick Actions After Deploy:
1. Visit your Railway URL to see the landing page
2. Update Stripe payment links in src/landing_page.py
3. Push changes to GitHub (auto-deploys)
4. Start marketing!

## Troubleshooting:
- If build fails: Check logs in Railway dashboard
- Common issue: Missing dependencies → add to requirements.txt
- Port issues: Make sure using $PORT environment variable 