# 🚀 Admin Dashboard Railway Deployment Guide

This guide explains how to deploy your Telegram Bot Admin Dashboard to Railway alongside your existing bot.

## 📋 Prerequisites

- Existing Railway project with your Telegram bot
- Railway CLI installed (optional)
- Git repository connected to Railway

## 🏗️ Deployment Architecture

The setup runs both your **Telegram bot** and **admin dashboard** on the same Railway service:

```
Railway Service
├── 🤖 Telegram Bot (Background)
├── 🌐 Admin Dashboard API (Port 8000)
├── 📱 React Frontend (Static files)
└── 🗄️ Shared PostgreSQL Database
```

## 🚀 Automatic Deployment

### Option 1: Git Push (Recommended)

Your admin dashboard is already configured for automatic deployment. Simply push to your repository:

```bash
git add .
git commit -m "Deploy admin dashboard"
git push origin main
```

Railway will automatically:
1. ✅ Install Node.js and Python dependencies
2. ✅ Build the React frontend 
3. ✅ Start both bot and dashboard
4. ✅ Make dashboard available at your Railway domain

### Option 2: Railway CLI

If you prefer using Railway CLI:

```bash
railway up
```

## 🌐 Accessing Your Dashboard

Once deployed, your admin dashboard will be available at:

```
https://your-project-name.up.railway.app
```

**API Endpoints:**
- Dashboard: `https://your-domain.railway.app/`
- API Health: `https://your-domain.railway.app/api/health`
- Settings API: `https://your-domain.railway.app/api/admin/settings`

## 🔧 Configuration

### Environment Variables

Your dashboard uses the same environment variables as your bot:

```env
# Database (already configured)
DATABASE_URL=postgresql://...

# Bot credentials (already configured)  
BOT_TOKEN=7594970416:AAG...
ADMIN_CHAT_ID=6781611639
ADMIN_GROUP_ID=-1002705423131

# Stripe (already configured)
STRIPE_SECRET_KEY=rk_test_51RlYBd...
```

### Port Configuration

Railway automatically assigns the PORT environment variable. The dashboard will:
- ✅ Serve frontend at root URL (`/`)
- ✅ Serve API at `/api/*` endpoints
- ✅ Run bot in background (webhook/polling)

## 📁 File Structure

```
telegram_bot/admin_dashboard/
├── dist/                    # Built React app (auto-generated)
├── src/                     # React source code
├── api_server.py           # FastAPI backend
├── start_server.py         # Railway startup script
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
└── railway.json           # Railway configuration
```

## 🔍 Monitoring & Logs

### Railway Dashboard
1. Go to your Railway project
2. Click on your service
3. View logs in the "Logs" tab

### Health Check
Monitor deployment health:
```bash
curl https://your-domain.railway.app/api/health
```

### Bot Status
Check if bot is running:
```bash
# Look for these in Railway logs:
✅ Database connected
🤖 Starting Telegram bot...
✅ Bot thread started  
🌐 Starting admin dashboard...
```

## 🛠️ Troubleshooting

### Build Issues

**Frontend build fails:**
```bash
# Check Node.js version in logs
# Ensure package.json is valid
# Verify npm install succeeded
```

**Python dependencies fail:**
```bash
# Check requirements.txt
# Verify Python version compatibility
```

### Runtime Issues

**Dashboard not accessible:**
1. Check Railway service is running
2. Verify PORT environment variable
3. Check application logs for errors

**Bot not responding:**
1. Verify BOT_TOKEN is correct
2. Check webhook configuration
3. Monitor bot thread startup in logs

**Database connection issues:**
1. Verify DATABASE_URL is set
2. Check database service is running
3. Ensure migration ran successfully

### Common Solutions

**Clear Railway cache:**
```bash
railway project delete
# Re-deploy from scratch
```

**Manual build:**
```bash
# In admin_dashboard directory:
npm install
npm run build
python api_server.py
```

## 📊 Performance

### Resource Usage
- **Memory**: ~200-300MB (bot + dashboard)
- **CPU**: Minimal (event-driven)
- **Storage**: <100MB (static files)

### Scaling
Railway automatically handles:
- ✅ Traffic spikes
- ✅ Memory management  
- ✅ Process restarts
- ✅ Zero-downtime deploys

## 🔒 Security

### Authentication
- Admin dashboard ready for token-based auth
- Environment variables secured by Railway
- HTTPS automatically enabled

### Access Control
- Dashboard accessible from any IP
- Consider adding IP whitelist for production
- Bot webhook secured with token validation

## 🎯 Next Steps

1. **Access your dashboard** at Railway URL
2. **Configure bot settings** via web interface
3. **Create credit packages** for users
4. **Monitor performance** through dashboard analytics

Your admin dashboard is now live and ready to use! 🎉 