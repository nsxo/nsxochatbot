# Deployment Guide

This guide covers deploying the Telegram Paid Messaging Bot to production.

## Prerequisites

- Docker and Docker Compose installed
- Domain name (for webhook endpoint)
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL database (or use Docker Compose)
- Stripe account with API keys

## Deployment Options

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <your-repo>
cd telegram_bot
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your actual values
nano .env
```

3. **Update Docker Compose for production**
```yaml
# Add to docker-compose.yml for production:
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - webhook
```

4. **Start services**
```bash
docker-compose up -d

# Initialize database
docker-compose exec bot python setup_db.py

# Check logs
docker-compose logs -f bot
```

### Option 2: VPS Deployment

1. **Install dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip postgresql nginx certbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Setup PostgreSQL**
```bash
sudo -u postgres psql
CREATE DATABASE telegram_bot;
CREATE USER botuser WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_bot TO botuser;
\q
```

3. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location /stripe-webhook {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Create systemd services**

Bot service (`/etc/systemd/system/telegram-bot.service`):
```ini
[Unit]
Description=Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/telegram_bot
Environment="PATH=/home/botuser/telegram_bot/venv/bin"
ExecStart=/home/botuser/telegram_bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Webhook service (`/etc/systemd/system/telegram-webhook.service`):
```ini
[Unit]
Description=Telegram Webhook Server
After=network.target postgresql.service

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/telegram_bot
Environment="PATH=/home/botuser/telegram_bot/venv/bin"
ExecStart=/home/botuser/telegram_bot/venv/bin/python webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start services**
```bash
sudo systemctl enable telegram-bot telegram-webhook
sudo systemctl start telegram-bot telegram-webhook
```

### Option 3: Cloud Platforms

#### Heroku
1. Create `Procfile`:
```
bot: python bot.py
web: python webhook_server.py
```

2. Deploy:
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set BOT_TOKEN=your_token
# Set other environment variables
git push heroku main
```

#### AWS EC2
1. Launch EC2 instance (Ubuntu 22.04 recommended)
2. Follow VPS deployment steps
3. Configure security groups for ports 80, 443, 8000

#### Google Cloud Run
1. Build container:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/telegram-bot
```

2. Deploy:
```bash
gcloud run deploy --image gcr.io/PROJECT-ID/telegram-bot
```

## Post-Deployment

### 1. Configure Stripe Webhook

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-domain.com/stripe-webhook`
3. Select events: `checkout.session.completed`
4. Copy signing secret to `.env`

### 2. Test the Bot

```bash
# Test bot is running
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Test webhook
stripe listen --forward-to https://your-domain.com/stripe-webhook
```

### 3. Monitoring

#### Using Prometheus + Grafana
1. Add metrics endpoint to bot
2. Configure Prometheus scraping
3. Create Grafana dashboards

#### Using Sentry
```python
# Add to bot.py
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

### 4. Backups

Create backup script (`backup.sh`):
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup database
pg_dump $DATABASE_URL > $BACKUP_DIR/db_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_$DATE.sql s3://your-bucket/backups/

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /home/botuser/backup.sh
```

## Security Checklist

- [ ] Use strong passwords for database
- [ ] Enable firewall (ufw/iptables)
- [ ] Keep system updated
- [ ] Use SSL/TLS for all connections
- [ ] Restrict database access
- [ ] Regular security audits
- [ ] Monitor for suspicious activity
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets
- [ ] Regular backups

## Troubleshooting

### Bot not responding
```bash
# Check service status
sudo systemctl status telegram-bot

# Check logs
sudo journalctl -u telegram-bot -f

# Test database connection
psql $DATABASE_URL -c "SELECT 1"
```

### Webhook not receiving events
```bash
# Test webhook endpoint
curl -X POST https://your-domain.com/stripe-webhook

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Verify SSL certificate
openssl s_client -connect your-domain.com:443
```

### Performance issues
```bash
# Monitor resources
htop

# Check database queries
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity"

# Analyze slow queries
EXPLAIN ANALYZE SELECT ...
```

## Scaling

### Horizontal Scaling
1. Use PostgreSQL connection pooling
2. Deploy multiple bot instances
3. Use Redis for caching
4. Load balance webhook servers

### Vertical Scaling
1. Increase server resources
2. Optimize database queries
3. Use database indexes
4. Enable query caching

## Maintenance

### Daily
- Check logs for errors
- Monitor resource usage
- Verify backups completed

### Weekly
- Review security logs
- Update dependencies
- Check Stripe webhook logs

### Monthly
- Security updates
- Performance analysis
- Cost optimization
- User growth analysis 