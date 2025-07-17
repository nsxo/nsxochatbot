# 🚀 Telegram Premium Messaging Bot

> **Enterprise-grade Telegram bot with Stripe payments, credit system, and comprehensive admin panel**

## ✨ Key Features

- 💳 **Stripe Integration**: Secure payments with webhook automation
- 💬 **Smart Credit System**: Text (1), Photo (3), Voice (5) credits per message  
- ⏰ **Time Sessions**: Unlimited messaging during purchased time blocks
- 🔄 **Two-Way Communication**: Seamless admin-user message forwarding
- 📊 **Advanced Admin Panel**: User management, analytics, and configuration
- 🔒 **Premium Content**: Pay-to-unlock media with custom pricing
- 💰 **Auto-Recharge**: Automatic credit top-ups with saved payment methods
- 🎯 **Visual UX**: Progress bars, read receipts, typing indicators

## 🛠 Quick Setup

### Prerequisites
- Python 3.10+
- PostgreSQL database  
- Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- Stripe account with API keys

### Installation

```bash
# Clone and setup
git clone <your-repo> telegram_bot
cd telegram_bot

# Virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` file:
```env
# Required Configuration
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=postgresql://username:password@localhost:5432/telegram_bot_db
STRIPE_API_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
ADMIN_CHAT_ID=your_telegram_user_id_here

# Optional Settings
WEBHOOK_PORT=8000
```

### Database & Launch

```bash
# Initialize database
python setup_db.py

# Start the bot
python run.py

# Or use the launch script
./scripts/run_bot.sh

# Optional: Webhook server (separate terminal)
python webhook_server.py
```

## 🎯 Core Architecture

```
telegram_bot/
├── 📁 src/                    # Core application code
│   ├── bot.py                 # Main bot application
│   ├── config.py              # Configuration management
│   ├── database.py            # Database operations
│   ├── cache.py               # Redis caching system
│   ├── error_handler.py       # Error handling & monitoring
│   ├── enhanced_webhooks.py   # Advanced webhook processing
│   └── webhook_server.py      # Stripe webhook server
├── 📁 scripts/                # Utility scripts
│   ├── setup_db.py            # Database initialization
│   └── run_bot.sh             # Launch script
├── 📁 deployment/             # Deployment configurations
│   ├── Dockerfile             # Container configuration
│   ├── docker-compose.yml     # Multi-service setup
│   └── railway.json           # Railway deployment config
├── 📁 docs/                   # Documentation
│   ├── README.md              # Main documentation (this file)
│   ├── DEPLOYMENT.md          # Production deployment guide
│   ├── ADMIN_MENU_GUIDE.md    # Admin features
│   ├── ADMIN_UI_PREVIEW.md    # UI screenshots
│   ├── DATABASE_IMPROVEMENTS_GUIDE.md
│   ├── STRIPE_WEBHOOKS_GUIDE.md
│   ├── PERFORMANCE_IMPROVEMENTS.md
│   └── MULTI_USER_ADMIN_GUIDE.md
├── 📋 Configuration Files
│   ├── .env                   # Environment variables
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml         # Code quality tools
│   ├── run.py                 # Main entry point
│   └── setup_db.py            # Database setup entry point
└── 📁 venv/                   # Virtual environment
```

## 🔥 Enterprise Features

### For Users
- **💳 Flexible Payments**: Credits or time-based sessions
- **📱 Visual Experience**: Progress bars, balance widgets, status indicators
- **⚡ Quick Actions**: `/buy10`, `/buy25`, instant top-ups
- **🔄 Auto-Recharge**: Never run out of credits
- **🎫 Customer Portal**: Manage payment methods via `/billing`

### For Admins  
- **📊 Dashboard**: Real-time stats via `/admin`
- **👥 User Management**: `/users` - ban, edit credits, view details
- **💬 Conversation Hub**: `/conversations` - manage all user chats
- **⚙️ Settings Panel**: `/settings` - dynamic configuration
- **📈 Analytics**: Response times, popular features, revenue tracking

### Advanced Capabilities
- **🔒 Locked Content**: Custom pricing for premium media
- **🏷️ User Tiers**: New → Regular → VIP progression  
- **📱 Mini App**: React-based web interface (optional)
- **🔔 Smart Notifications**: Low balance warnings, session expiry alerts

## 💡 Quick Start Examples

### Add Products (via database)
```sql
-- Credit packages
INSERT INTO products (label, stripe_price_id, item_type, amount, is_active) 
VALUES ('10 Credits Pack', 'price_xxxxxxxxxxxxxx', 'credits', 10, true);

-- Time sessions (3600 seconds = 1 hour)
INSERT INTO products (label, stripe_price_id, item_type, amount, is_active) 
VALUES ('1 Hour Chat', 'price_yyyyyyyyyyyyyy', 'time', 3600, true);
```

### Essential Admin Commands
```bash
/admin          # Main admin dashboard
/settings       # Bot configuration
/users          # User management  
/conversations  # Chat management
/dashboard      # Analytics overview
```

### User Commands
```bash
/start          # Get started & view packages
/balance        # Check credits/time remaining
/billing        # Manage payment methods
/autorecharge   # Configure auto top-ups
/purchases      # View locked content
```

## 🚀 Production Deployment

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway link
railway up
```

### Docker
```bash
# Build and run
docker-compose up -d

# Or single container
docker build -t telegram-bot .
docker run -d --env-file .env telegram-bot
```

### Manual VPS
```bash
# Install as systemd service
sudo cp telegram_bot.service /etc/systemd/system/
sudo systemctl enable telegram_bot
sudo systemctl start telegram_bot
```

## 📊 Performance Features

- **🔄 Connection Pooling**: Optimized database connections
- **💾 Redis Caching**: Settings and user data caching  
- **📈 Error Monitoring**: Comprehensive logging and alerts
- **⚡ Rate Limiting**: Anti-spam protection
- **🔍 SQL Optimization**: Indexed queries and batch operations

## 🛡️ Security & Compliance

- **🔐 Stripe Security**: PCI-compliant payment processing
- **🔒 Data Protection**: Encrypted sensitive data storage
- **🚫 Access Control**: Admin-only commands and rate limiting
- **📝 Audit Logging**: Complete transaction and action logs

## 📚 Advanced Documentation

- **[Deployment Guide](DEPLOYMENT.md)**: Production setup and scaling
- **[Performance Guide](PERFORMANCE_IMPROVEMENTS.md)**: Optimization techniques  
- **[Database Guide](DATABASE_IMPROVEMENTS_GUIDE.md)**: Schema and queries
- **[Webhook Guide](STRIPE_WEBHOOKS_GUIDE.md)**: Payment integration
- **[Admin Guide](ADMIN_UI_PREVIEW.md)**: Admin panel features

## 📞 Support & Maintenance

**Quick Diagnostics:**
```bash
# Check bot status
tail -f bot.log

# Database health
python -c "from database import db_manager; print('DB OK' if db_manager.test_connection() else 'DB Error')"

# Test Stripe connection  
python -c "import stripe; stripe.api_key='your_key'; print(stripe.Account.retrieve())"
```

**Common Issues:**
- Database connection errors → Check `DATABASE_URL` 
- Stripe webhook failures → Verify `STRIPE_WEBHOOK_SECRET`
- Permission denied → Confirm `ADMIN_CHAT_ID` is correct

---

🎉 **Ready to launch your premium Telegram bot!** For support or feature requests, check the documentation or create an issue.