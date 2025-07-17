# Telegram Mini App Deployment Guide

## 🚀 Quick Start

This guide will help you deploy your NSXoChat Mini App and integrate it with your Telegram bot.

## 📋 Prerequisites

- ✅ Node.js 18+ installed
- ✅ Domain with HTTPS certificate (required for Mini Apps)
- ✅ Telegram Bot Token
- ✅ Stripe account for payments
- ✅ PostgreSQL database

## 🛠️ Local Development Setup

### 1. Install Dependencies

```bash
cd webapp
npm install
```

### 2. Configure Environment

Create `.env.local` file:

```env
NODE_ENV=development
VITE_API_BASE_URL=http://localhost:8000/api
VITE_BOT_TOKEN=your_bot_token_here
```

### 3. Start Development Server

```bash
npm run dev
```

Your app will be available at `http://localhost:3000`

## 🌐 Production Deployment

### Option 1: Vercel (Recommended)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   cd webapp
   vercel --prod
   ```

3. **Configure Environment Variables in Vercel:**
   - `VITE_API_BASE_URL=https://your-domain.com/api`
   - `VITE_BOT_TOKEN=your_bot_token`

### Option 2: Netlify

1. **Build the app:**
   ```bash
   npm run build
   ```

2. **Deploy to Netlify:**
   - Drag `dist/` folder to Netlify dashboard
   - Or connect your GitHub repository

### Option 3: Traditional VPS

1. **Build the app:**
   ```bash
   npm run build
   ```

2. **Upload to your server:**
   ```bash
   scp -r dist/* user@your-server:/var/www/your-domain/
   ```

3. **Nginx Configuration:**
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/private.key;
       
       root /var/www/your-domain;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🔧 Bot Integration

### 1. Install Flask Dependencies

```bash
cd telegram_bot
pip install flask flask-cors
```

### 2. Update Bot Configuration

Add to your `bot.py`:

```python
from miniapp_integration import register_miniapp_handlers, add_miniapp_button

# Register Mini App handlers
register_miniapp_handlers(application)

# Update your start command to include Mini App button
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await add_miniapp_button(update, context)
```

### 3. Start API Server

Run the Mini App API server:

```bash
cd telegram_bot
python miniapp_api.py
```

### 4. Update Configuration

Edit `miniapp_integration.py`:

```python
# Replace with your deployed Mini App URL
MINI_APP_URL = "https://your-domain.com"
```

Edit `miniapp_api.py`:

```python
# Replace with your bot token
BOT_TOKEN = "your_actual_bot_token"

# Update CORS origins
CORS(app, origins=["http://localhost:3000", "https://your-domain.com"])
```

## 🔐 Security Configuration

### 1. Environment Variables

**Production `.env.production`:**
```env
NODE_ENV=production
VITE_API_BASE_URL=https://your-domain.com/api
```

### 2. HTTPS Requirements

⚠️ **Important:** Telegram Mini Apps require HTTPS in production.

- Use SSL certificate (Let's Encrypt recommended)
- Configure proper CORS headers
- Validate WebApp init data server-side

### 3. Rate Limiting

Add rate limiting to your API:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 📱 Testing the Mini App

### 1. Test Locally

1. Start both servers:
   ```bash
   # Terminal 1 - Mini App
   cd webapp && npm run dev
   
   # Terminal 2 - API Server
   cd telegram_bot && python miniapp_api.py
   ```

2. Test in Telegram:
   - Send `/start` to your bot
   - Tap "🚀 Open NSXoChat App"

### 2. Test in Production

1. Deploy Mini App to your domain
2. Update bot configuration with production URL
3. Restart bot
4. Test all features

## 🔍 Troubleshooting

### Common Issues

**1. Mini App doesn't load:**
- ✅ Check HTTPS certificate
- ✅ Verify CORS configuration
- ✅ Check browser console for errors

**2. API calls fail:**
- ✅ Verify API server is running
- ✅ Check network connectivity
- ✅ Validate WebApp init data

**3. Payments don't work:**
- ✅ Configure Stripe webhooks
- ✅ Test with Stripe test keys first
- ✅ Check webhook endpoints

### Debug Mode

Enable debug logging:

```python
# In miniapp_api.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring

### Performance Monitoring

Add monitoring to track:
- Mini App load times
- API response times
- Error rates
- User engagement

### Analytics

Consider adding:
- Google Analytics
- Telegram Analytics
- Custom event tracking

## 🔄 Updates

### Deploying Updates

1. **Frontend Updates:**
   ```bash
   npm run build && vercel --prod
   ```

2. **Backend Updates:**
   ```bash
   # Restart bot process
   systemctl restart telegram-bot
   
   # Restart API server
   systemctl restart miniapp-api
   ```

### Zero-Downtime Deployment

Use tools like PM2 for Node.js or systemd for Python services.

## 📚 Additional Resources

- [Telegram Mini Apps Documentation](https://core.telegram.org/bots/webapps)
- [React Documentation](https://react.dev/)
- [Vercel Deployment Guide](https://vercel.com/docs)
- [Stripe Integration Guide](https://stripe.com/docs)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review server logs
3. Test in development environment
4. Verify all configuration values

---

**🎉 Congratulations!** Your Telegram Mini App should now be deployed and ready to provide an enhanced user experience! 