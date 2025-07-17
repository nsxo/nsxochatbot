# Multi-User Conversation Management Guide

## 🎯 Overview

The bot now includes a powerful **Conversation Management System** that helps admins efficiently handle multiple users chatting simultaneously. This guide explains how to use all the new features.

## 🚀 Getting Started

### 1. Update Your Database
Run the database setup to add the conversations table:
```bash
cd telegram_bot
python setup_db.py
```

### 2. Access Conversation Management
- **`/conversations`** - View all active conversations
- **`/dashboard`** - See conversation stats in admin dashboard

## 📋 Main Features

### 🎯 **Priority System**
Conversations are automatically prioritized based on:
- **User Tier**: VIP (30 pts) > Regular (20 pts) > New (10 pts)
- **Credit Urgency**: No credits (+25), Low credits (+15), High balance (+10)
- **Purchase History**: 20+ purchases (+15), 10+ purchases (+10), 5+ purchases (+5)
- **Max Priority**: 100 points

### 📊 **Visual Indicators**
- **🔥** High priority (50+ points)
- **📌** Pinned conversations
- **(3)** Unread message count
- **@username** User identification
- **⭐ Regular / 🏆 VIP** User tier badges

## 💬 Using /conversations Command

### Main View
```
💬 Active Conversations

📌🔥 1. @alice123 🏆 VIP
   💬 12 msgs (3) • 5m ago
   _Hey, I need help with my purchase..._

2. @bob456 ⭐ Regular
   💬 8 msgs (1) • 15m ago
   _Quick question about credits..._

3. @newuser 🆕 New
   💬 2 msgs (2) • 1h ago
   _Hello! How does this work?_
```

### Navigation Buttons
- **[Username (3)]** - Manage specific conversation
- **[📋 View All]** - See up to 50 conversations
- **[📦 Archived]** - View archived conversations
- **[🔄 Refresh]** - Update the list

## 🛠️ Conversation Management

### Individual Conversation Actions
Click any username to access:

```
👤 Conversation: @alice123

Tier: 🏆 VIP
Priority: 85/100
Total Messages: 12
Unread: 3
Last Message: 5m ago
Pinned: Yes

💬 Last message:
_Hey, I need help with my purchase..._

[📌 Unpin] [📝 Add Note]
[📦 Archive] [✅ Mark Read]
[👤 User Info] [💬 Direct Message]
[⬅️ Back]
```

### Available Actions

#### 📌 **Pin/Unpin**
- Pinned conversations appear at the top
- Use for urgent or important conversations
- Survives page refreshes

#### 📝 **Add Note** (Future Feature)
- Add private notes about the conversation
- Helps track context across sessions
- Only visible to admin

#### 📦 **Archive**
- Move finished conversations to archive
- Keeps main list clean
- Can be restored later

#### ✅ **Mark as Read**
- Reset unread counter to 0
- Useful for bulk management
- Updates last admin reply timestamp

#### 👤 **User Info**
- Quick access to user details
- Shows tier, credits, purchase history
- Same as existing user info popup

#### 💬 **Direct Message** (Future Feature)
- Start typing to this user immediately
- Context-aware messaging

## 📈 Enhanced Dashboard

The `/dashboard` command now shows:

```
📊 Admin Dashboard

👥 Total Users: 156
✅ Active Users: 142
🚫 Banned Users: 14

💬 Active Conversations: 8
📬 Unread Messages: 12

💰 Total Credits: 12,450
⏰ Total Time: 324h

[💬 Conversations] [📊 Detailed Stats]
[📢 Broadcast] [🎁 Mass Gift]
[⚙️ Settings] [🔄 Refresh]
```

## 🔄 Real-Time Updates

### Automatic Tracking
The system automatically:
- ✅ **Tracks every user message** (increments counters)
- ✅ **Updates last message time** (for sorting)
- ✅ **Calculates priority** (based on user context)
- ✅ **Resets unread count** (when admin replies)
- ✅ **Preserves message preview** (last 500 characters)

### Message Flow
1. **User sends message** → Counter increments, priority calculated
2. **Admin replies** → Unread count resets, reply timestamp updated
3. **Conversation sorted** → By pinned > priority > unread > time

## 🎛️ Admin Workflow Examples

### 📞 **Handling High Volume**
1. Type `/conversations` to see priority list
2. Focus on 🔥 high-priority or pinned 📌 conversations first
3. Use quick replies for common responses
4. Archive ✅ completed conversations

### 🎯 **VIP Customer Management**
1. VIP customers automatically get high priority
2. Pin important VIP conversations
3. Use notes to track their preferences
4. Quick access to their purchase history

### 🧹 **Daily Cleanup**
1. Review `/conversations` for old conversations
2. Archive resolved issues
3. Pin ongoing important discussions
4. Check archived conversations weekly

## 🚀 Advanced Tips

### **Multi-Tab Workflow**
- Keep `/conversations` open in one chat
- Use quick action buttons for rapid responses
- Refresh periodically to see new messages

### **Priority Optimization**
- High-value customers (50+ credits) get priority boost
- Zero-credit users get urgent priority (need attention!)
- Purchase history affects long-term priority

### **Conversation Hygiene**
- Archive completed conversations daily
- Pin urgent/ongoing issues
- Use notes for complex customer situations

## 🔮 Coming Soon

### Planned Features
- **📝 Conversation Notes** - Add private admin notes
- **⏰ Snooze Conversations** - Hide until later
- **📱 Push Notifications** - Real-time alerts
- **📊 Conversation Analytics** - Response time tracking
- **🏷️ Conversation Tags** - Categorize discussions
- **🔍 Search Conversations** - Find by username/content

## 🛠️ Technical Details

### Database Schema
```sql
conversations (
    user_id BIGINT PRIMARY KEY,
    last_message_at TIMESTAMP,
    total_messages INT DEFAULT 0,
    unread_messages INT DEFAULT 0,
    conversation_status VARCHAR(20) DEFAULT 'active',
    priority_level INT DEFAULT 0,
    last_user_message TEXT,
    last_admin_reply_at TIMESTAMP,
    is_pinned BOOLEAN DEFAULT FALSE,
    notes TEXT
)
```

### Performance
- Indexed by status, priority, and message time
- Efficient queries for up to 1000+ conversations
- Real-time updates without database locking

## 🔧 Troubleshooting

### Common Issues

**"No conversations found"**
- Users need to send at least one message to appear
- Check if database table was created (`python setup_db.py`)

**"Conversation not found"**
- User may have been deleted from database
- Check user still exists in users table

**Priority seems wrong**
- Priority recalculates on each message
- Based on tier, credits, and purchase history
- Check user's current tier in User Info

### Debug Commands
```bash
# Check conversation table
psql $DATABASE_URL -c "SELECT * FROM conversations LIMIT 5;"

# Check recent activity
psql $DATABASE_URL -c "SELECT user_id, last_message_at, unread_messages FROM conversations ORDER BY last_message_at DESC LIMIT 10;"
```

## 📞 Support

For issues with the conversation management system:
1. Check the bot logs for errors
2. Verify database schema is up to date
3. Test with a single conversation first
4. Restart the bot if needed

The conversation system is designed to handle high-volume scenarios while keeping the admin experience smooth and organized. 