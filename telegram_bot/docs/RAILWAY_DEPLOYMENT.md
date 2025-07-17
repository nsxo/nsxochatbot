# Railway Deployment Guide

This guide will walk you through deploying your Telegram bot and database to Railway, a modern platform for deploying applications with minimal configuration.

## 🚀 Why Railway?

- **Automatic PostgreSQL database** provisioning
- **Zero-config deployments** from GitHub
- **Built-in monitoring** and logging
- **Automatic SSL certificates**
- **Environment variable management**
- **Pay-as-you-scale** pricing

## 📋 Prerequisites

Before you start, make sure you have:

- [x] A GitHub account with your bot code
- [x] A Telegram bot token from [@BotFather](https://t.me/BotFather)
- [x] A Stripe account with API keys
- [x] Your Telegram user ID (get it from [@userinfobot](https://t.me/userinfobot))

## 🛠️ Step 1: Prepare Your Repository

1. **Commit all your changes**:
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Verify Railway configuration files**:
   - ✅ `deployment/railway.json` (Railway config)
   - ✅ `deployment/Dockerfile` (Container config)
   - ✅ `deployment/railway_start.py` (Startup script)
   - ✅ `deployment/railway_init_db.py` (Database setup)
   - ✅ `deployment/railway.env.example` (Environment template)

## 🌐 Step 2: Create Railway Project

1. **Sign up for Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account

2. **Create a new project**:
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your bot repository
   - Railway will automatically detect the Dockerfile

3. **Configure project settings**:
   - Set the **Root Directory** to `telegram_bot/` if prompted
   - Railway will use the Dockerfile in `deployment/Dockerfile`

## 🗃️ Step 3: Add PostgreSQL Database

1. **Add PostgreSQL service**:
   - In your Railway project dashboard
   - Click "Add Service" or "+"
   - Select "PostgreSQL"
   - Railway will automatically provision a database

2. **Note the database connection**:
   - The database URL will be automatically available as `${{Postgres.DATABASE_URL}}`
   - Your bot will automatically connect to this database

## ⚙️ Step 4: Configure Environment Variables

1. **Access environment variables**:
   - In your Railway project
   - Click on your bot service
   - Go to the "Variables" tab

2. **Add required variables**:

   ```bash
   # Required Bot Configuration
   BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789
   ADMIN_CHAT_ID=123456789
   
   # Database (automatically set by Railway)
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   
   # Stripe Configuration
   STRIPE_API_KEY=sk_test_123456789abcdefghijklmnopqrstuvwxyz
   STRIPE_WEBHOOK_SECRET=whsec_abcdefghijklmnopqrstuvwxyz123456789
   
   # Optional Configuration
   LOG_LEVEL=INFO
   WEBHOOK_PORT=8000
   ```

3. **Important notes**:
   - Replace the example bot token with your actual bot token from @BotFather
   - Replace the example user ID with your actual Telegram user ID
   - Get Stripe keys from your [Stripe Dashboard](https://dashboard.stripe.com)
   - Don't change `DATABASE_URL` - Railway sets this automatically

## 🚀 Step 5: Deploy Your Bot

1. **Deploy the application**:
   - Railway will automatically deploy when you push to your main branch
   - Or click "Deploy" in the Railway dashboard
   - Watch the build logs in real-time

2. **Monitor the deployment**:
   - Check the "Deployments" tab for progress
   - View logs in the "Logs" tab
   - Look for "✅ Database initialization completed" message

3. **Verify bot is running**:
   - Check logs for "Bot starting..." message
   - Check logs for "Starting webhook server..." message
   - Test your bot by sending `/start` in Telegram

## 🔗 Step 6: Configure Stripe Webhook

1. **Get your Railway domain**:
   - In Railway dashboard, click on your service
   - Go to "Settings" tab
   - Copy the "Public Domain" URL (e.g., `https://your-app.railway.app`)

2. **Add Stripe webhook**:
   - Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
   - Click "Add endpoint"
   - Enter endpoint URL: `https://your-app.railway.app/stripe-webhook`
   - Select events: `checkout.session.completed`
   - Copy the signing secret and update `STRIPE_WEBHOOK_SECRET` in Railway

3. **Test the webhook**:
   - Use Stripe CLI: `stripe listen --forward-to https://your-app.railway.app/stripe-webhook`
   - Or make a test purchase through your bot

## 📊 Step 7: Monitor Your Deployment

### Health Checks
- Railway automatically monitors your app's health
- Health endpoint: `https://your-app.railway.app/health`
- Should return `{"status": "healthy"}`

### Logs and Monitoring
- **View logs**: Railway dashboard → your service → "Logs" tab
- **Monitor metrics**: Check CPU, memory, and network usage
- **Set up alerts**: Configure notifications for failures

### Database Management
- **Access database**: Railway dashboard → PostgreSQL service
- **View connection info**: Check environment variables
- **Monitor performance**: View database metrics

## 🔧 Common Issues and Solutions

### Bot Not Starting
```bash
# Check these in Railway logs:
❌ "Missing required environment variables"
→ Solution: Verify all required env vars are set

❌ "Database connection failed"
→ Solution: Ensure PostgreSQL service is running and DATABASE_URL is correct

❌ "BOT_TOKEN not found"
→ Solution: Double-check your bot token from @BotFather
```

### Webhook Issues
```bash
❌ "Stripe signature verification failed"
→ Solution: Verify STRIPE_WEBHOOK_SECRET matches Stripe dashboard

❌ "Webhook endpoint not found"
→ Solution: Ensure your Railway domain is correctly set in Stripe
```

### Database Issues
```bash
❌ "relation 'users' does not exist"
→ Solution: Database initialization failed, check logs and redeploy

❌ "connection pool exhausted"
→ Solution: Check for connection leaks, restart the service
```

## 🔄 Step 8: Updates and Maintenance

### Deploying Updates
```bash
# Automatic deployment on git push:
git add .
git commit -m "Update bot features"
git push origin main
# Railway will automatically deploy the changes
```

### Manual Deployment
- Go to Railway dashboard
- Click your service → "Deployments" tab
- Click "Deploy" button

### Environment Variable Updates
- Railway dashboard → your service → "Variables" tab
- Add/edit variables
- Service will automatically restart with new variables

### Database Backups
- Railway automatically backs up PostgreSQL databases
- Access backups: PostgreSQL service → "Data" tab
- Manual backup: Use `pg_dump` with Railway database URL

## 🎯 Step 9: Production Best Practices

### Security
- [ ] **Use production Stripe keys** (start with `sk_live_`)
- [ ] **Enable Stripe webhook signature verification**
- [ ] **Set strong database passwords** (Railway does this automatically)
- [ ] **Monitor logs for suspicious activity**

### Performance
- [ ] **Monitor resource usage** in Railway dashboard
- [ ] **Set up database connection pooling** (already configured)
- [ ] **Enable Redis for caching** (add Redis service in Railway)
- [ ] **Monitor response times** for webhook endpoints

### Monitoring
- [ ] **Set up Sentry** for error tracking (add `SENTRY_DSN` env var)
- [ ] **Configure log retention** in Railway settings
- [ ] **Set up uptime monitoring** (Railway provides this)
- [ ] **Monitor Stripe webhook delivery** in Stripe dashboard

## 📈 Scaling Your Bot

### Vertical Scaling
- Railway automatically scales based on usage
- Monitor CPU and memory in the dashboard
- Upgrade plan if needed for higher limits

### Horizontal Scaling
- Consider multiple bot instances for high traffic
- Use Redis for shared state management
- Implement proper session handling

### Database Optimization
- Monitor slow queries in PostgreSQL logs
- Add database indexes for frequently queried columns
- Consider read replicas for heavy read workloads

## 💰 Cost Management

### Railway Pricing
- **Hobby Plan**: $5/month + usage-based pricing
- **Pro Plan**: $20/month + usage-based pricing
- **Team Plan**: $50/month + usage-based pricing

### Cost Optimization
- Monitor usage in Railway dashboard
- Set up billing alerts
- Optimize database queries to reduce CPU usage
- Use environment variables to toggle features

## 🔗 Useful Links

- [Railway Documentation](https://docs.railway.app)
- [Railway Templates](https://railway.app/templates)
- [PostgreSQL on Railway](https://docs.railway.app/databases/postgresql)
- [Environment Variables](https://docs.railway.app/develop/variables)
- [Custom Domains](https://docs.railway.app/deploy/custom-domains)

## 🆘 Getting Help

- **Railway Support**: [Railway Discord](https://discord.gg/railway)
- **Bot Issues**: Check the logs in Railway dashboard
- **Stripe Issues**: [Stripe Support](https://support.stripe.com)
- **General Questions**: Create an issue in your repository

---

## 🎉 Success Checklist

After following this guide, you should have:

- [x] ✅ Bot deployed and running on Railway
- [x] ✅ PostgreSQL database configured and initialized
- [x] ✅ All environment variables properly set
- [x] ✅ Stripe webhook configured and working
- [x] ✅ Health checks passing
- [x] ✅ Bot responding to `/start` command
- [x] ✅ Payment processing working
- [x] ✅ Logs showing no errors

**Congratulations! Your Telegram bot is now running on Railway! 🚀** 