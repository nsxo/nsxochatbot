# 🚀 Quick Railway Environment Setup Guide

Your Railway deployment is working perfectly, but missing environment variables. Here's how to fix it:

## 🔧 Step 1: Get Your Values

### **Bot Token** (Required)
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/mybots`
3. Select your bot
4. Click "API Token"
5. Copy the token (format: `1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi`)

### **Admin Chat ID** (Required)
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your user ID (numeric, like `123456789`)

### **Database** (Railway handles this)
- Railway automatically provides `DATABASE_URL` when you add PostgreSQL
- You just need to add a PostgreSQL service to your project

## 🗄️ Step 2: Add PostgreSQL to Railway

1. **In Railway Dashboard**:
   - Go to your project
   - Click **"+ New Service"**
   - Select **"PostgreSQL"**
   - Railway will automatically provision the database

2. **Connect Database**:
   - Railway automatically sets `DATABASE_URL` variable
   - Your bot will connect automatically

## ⚙️ Step 3: Set Environment Variables

1. **In Railway Dashboard**:
   - Click on your **bot service** (not database)
   - Go to **"Variables"** tab
   - Click **"+ New Variable"**

2. **Add these variables**:

```bash
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi
ADMIN_CHAT_ID=123456789
```

3. **Optional variables** (for payments):
```bash
STRIPE_API_KEY=sk_test_your_stripe_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

## 🚀 Step 4: Verify Deployment

After setting variables, Railway will automatically redeploy. Look for:

```bash
🚀 Starting Enhanced Railway Bot
🤖 Bot Token: ✅ Set
👨‍💼 Admin ID: ✅ Set
🗄️ Database: ✅ Set
✅ Bot setup completed successfully!
```

## 🧪 Step 5: Test Your Bot

1. **Find your bot** on Telegram (the username you set with BotFather)
2. **Send `/start`** - should get welcome message and credit packages
3. **Send `/help`** - should show all available commands
4. **Admin test**: Send `/admin` - should show admin panel (only for you)

## 🔍 Troubleshooting

### If bot still shows "Missing" values:
1. **Double-check variable names** (case-sensitive)
2. **Verify no extra spaces** in values
3. **Check Railway logs** for specific error messages

### Common Issues:
- **Bot token format**: Must be `numbers:letters` format
- **Admin ID format**: Must be numbers only (your user ID)
- **Database**: Make sure PostgreSQL service is running

## 🎉 Success Indicators

When everything works, you'll see:
- ✅ Health check passing
- ✅ No "Missing" environment variables  
- ✅ Bot responds to `/start` command
- ✅ Admin commands work (if you're the admin)

**Your deployment architecture is solid - just needs the environment variables!** 🚀 