# 🤖 Telegram Bot with Topic Management

A professional Telegram bot with advanced topic management, Stripe payments, and admin tools.

## ✨ Features

- **Topic Management**: Dedicated conversation threads for each user
- **Stripe Integration**: Credit-based messaging with payment processing
- **Admin Tools**: Comprehensive admin panel with analytics
- **Railway Deployment**: Production-ready deployment configuration
- **Webhook Support**: Optimized for webhook-based message handling

## 📁 Project Structure

```
telegram_bot/
├── src/                    # Core application code
│   ├── bot.py             # Main bot application
│   ├── config.py          # Configuration management
│   ├── database.py        # Database operations
│   ├── webhook_server.py  # Flask webhook server
│   └── ...
├── deployment/            # Deployment configurations
│   ├── simple_railway_bot.py  # Railway webhook bot
│   ├── Dockerfile         # Docker configuration
│   └── railway.env.example    # Environment template
├── docs/                  # Documentation
│   ├── README.md          # Main documentation
│   ├── RAILWAY_DEPLOYMENT.md  # Deployment guide
│   └── ...
├── scripts/               # Utility scripts
│   ├── setup_webhook.py   # Webhook configuration
│   └── run_bot.sh        # Bot startup script
├── requirements.txt       # Python dependencies
├── railway.json          # Railway deployment config
└── pyproject.toml        # Python project configuration
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and setup
git clone https://github.com/nsxo/nsxochatbot.git
cd nsxochatbot/telegram_bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy `deployment/railway.env.example` to `.env` and configure:

```bash
cp deployment/railway.env.example .env
```

Required environment variables:
- `BOT_TOKEN`: From @BotFather
- `ADMIN_CHAT_ID`: Your Telegram user ID
- `ADMIN_GROUP_ID`: Admin group for topics
- `DATABASE_URL`: PostgreSQL connection string
- `STRIPE_API_KEY`: Stripe API key
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret

### 3. Database Setup

```bash
python scripts/setup_db.py
```

### 4. Local Development

```bash
# Run locally (polling mode)
python run.py

# Or run with webhook server
python src/webhook_server.py
```

### 5. Railway Deployment

```bash
# Connect to Railway
railway login
railway link

# Deploy
git push origin main
```

## 📚 Documentation

- **[Deployment Guide](docs/RAILWAY_DEPLOYMENT.md)** - Complete Railway setup
- **[Topic System](docs/TOPIC_SYSTEM_DEPLOYMENT_SUMMARY.md)** - Topic management features
- **[Admin Guide](docs/ADMIN_MENU_GUIDE.md)** - Admin panel usage
- **[Database Guide](docs/DATABASE_IMPROVEMENTS_GUIDE.md)** - Database management
- **[Improvements Roadmap](docs/ADVANCED_IMPROVEMENTS_ROADMAP.md)** - Future enhancements

## 🛠️ Development

### Key Files

- **`src/bot.py`**: Main bot logic with all handlers
- **`src/config.py`**: Centralized configuration
- **`src/database.py`**: Database operations and models
- **`deployment/simple_railway_bot.py`**: Production webhook bot

### Topic Management

The bot creates dedicated topics for each user in the admin group:
- Automatic topic creation
- User info cards with analytics
- Direct admin replies through topics
- Message forwarding and tracking

### Payment System

Integrated Stripe payments for credit-based messaging:
- Multiple credit packages
- Automatic credit allocation
- Webhook-based payment processing
- Purchase history tracking

## 🔧 Scripts

- **`scripts/setup_webhook.py`**: Configure Telegram webhooks
- **`scripts/setup_db.py`**: Initialize database schema
- **`scripts/run_bot.sh`**: Production startup script

## 📊 Monitoring

- **Health Check**: `/health` endpoint
- **Bot Status**: Webhook vs polling mode detection
- **Error Tracking**: Comprehensive error handling
- **Analytics**: Built-in admin analytics

## 🎯 Current Status

- ✅ **Topic Management**: Fully implemented and deployed
- ✅ **Railway Deployment**: Production ready
- ✅ **Webhook Mode**: Optimized for Railway
- ✅ **Payment Integration**: Stripe webhooks configured
- ✅ **Admin Tools**: Comprehensive admin panel

## 🔮 Future Enhancements

See [Advanced Improvements Roadmap](docs/ADVANCED_IMPROVEMENTS_ROADMAP.md) for planned features:
- AI-powered message categorization
- Multi-admin collaboration
- Advanced analytics dashboard
- Mobile admin app

---

**Bot Username**: @nsxochatbot  
**Deployment**: https://nsxomsgbot-production.up.railway.app  
**Admin Group**: Configured for topic management 