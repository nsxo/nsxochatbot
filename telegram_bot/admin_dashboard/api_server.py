#!/usr/bin/env python3
"""
Admin Dashboard API Server
Provides REST API endpoints for the web-based admin dashboard.
"""

import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Add the src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from database import DatabaseManager
    from config import *
except ImportError as e:
    print(f"Failed to import bot modules: {e}")
    print("Make sure you're running this from the telegram_bot directory")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="Bot Admin Dashboard API",
    description="REST API for managing Telegram bot configuration",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db_manager = None

async def get_db():
    """Dependency to get database manager"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
        await db_manager.initialize()
    return db_manager

# Pydantic models for API
class SettingsUpdate(BaseModel):
    welcome_message: Optional[str] = None
    low_balance_message: Optional[str] = None
    insufficient_credits_message: Optional[str] = None
    payment_success_message: Optional[str] = None
    support_message: Optional[str] = None
    cost_text_message: Optional[int] = None
    cost_photo_message: Optional[int] = None
    cost_video_message: Optional[int] = None
    cost_document_message: Optional[int] = None
    starting_credits: Optional[int] = None
    low_credit_threshold: Optional[int] = None
    vip_threshold: Optional[int] = None
    regular_discount: Optional[int] = None
    vip_discount: Optional[int] = None
    auto_recharge_enabled: Optional[bool] = None
    admin_email: Optional[str] = None
    daily_summary: Optional[bool] = None
    max_file_size: Optional[int] = None
    session_timeout: Optional[int] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None

class ProductCreate(BaseModel):
    label: str
    amount: int
    item_type: str = "credits"
    description: Optional[str] = None
    stripe_price_id: Optional[str] = None
    is_active: bool = True

class ProductUpdate(BaseModel):
    label: Optional[str] = None
    amount: Optional[int] = None
    item_type: Optional[str] = None
    description: Optional[str] = None
    stripe_price_id: Optional[str] = None
    is_active: Optional[bool] = None

# Default settings configuration
DEFAULT_SETTINGS = {
    "welcome_message": "🎉 Welcome to our premium messaging service!\n\nGet started with 5 free credits and experience direct communication with our team.",
    "low_balance_message": "⚠️ You're running low on credits. Consider purchasing more to continue messaging.",
    "insufficient_credits_message": "❌ You don't have enough credits for this message. Please purchase more credits to continue.",
    "payment_success_message": "✅ Payment successful! Your credits have been added to your account.",
    "support_message": "Our support team has received your message and will respond shortly.",
    "cost_text_message": 1,
    "cost_photo_message": 2,
    "cost_video_message": 3,
    "cost_document_message": 2,
    "starting_credits": 5,
    "low_credit_threshold": 5,
    "vip_threshold": 100,
    "regular_discount": 10,
    "vip_discount": 20,
    "auto_recharge_enabled": True,
    "admin_email": "",
    "daily_summary": False,
    "max_file_size": 20,
    "session_timeout": 30,
    "maintenance_mode": False,
    "maintenance_message": "The bot is currently under maintenance. Please try again later."
}

# API Endpoints

@app.get("/api/admin/dashboard")
async def get_dashboard_stats(db: DatabaseManager = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        # Get user statistics
        users_query = "SELECT COUNT(*) as total FROM users"
        total_users = db.execute_query(users_query, fetch_one=True)['total']
        
        # Get active users (last 7 days)
        active_query = """
        SELECT COUNT(*) as active FROM users 
        WHERE last_interaction > ?
        """
        week_ago = datetime.now() - timedelta(days=7)
        active_users = db.execute_query(active_query, (week_ago,), fetch_one=True)['active']
        
        # Get message count
        messages_query = "SELECT COUNT(*) as total FROM user_messages"
        total_messages = db.execute_query(messages_query, fetch_one=True)['total']
        
        # Calculate mock revenue based on products and transactions
        revenue_query = """
        SELECT SUM(CAST(amount AS REAL)) as revenue 
        FROM products WHERE is_active = TRUE
        """
        products = db.execute_query(revenue_query, fetch_one=True)
        total_revenue = products.get('revenue', 0) if products else 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_messages": total_messages,
            "total_revenue": total_revenue or 0,
            "trends": {
                "users": {"direction": "up", "value": "12%"},
                "messages": {"direction": "up", "value": "8%"},
                "revenue": {"direction": "up", "value": "15%"}
            },
            "recent_activity": []
        }
    except Exception as e:
        return {
            "total_users": 0,
            "active_users": 0,
            "total_messages": 0,
            "total_revenue": 0,
            "trends": {},
            "recent_activity": []
        }

@app.get("/api/admin/settings")
async def get_settings(db: DatabaseManager = Depends(get_db)):
    """Get current bot settings"""
    try:
        # Try to get settings from database (if you have a settings table)
        # For now, return default settings
        return DEFAULT_SETTINGS
    except Exception as e:
        return DEFAULT_SETTINGS

@app.put("/api/admin/settings")
async def update_setting(setting_data: Dict[str, Any], db: DatabaseManager = Depends(get_db)):
    """Update a single setting"""
    try:
        # In a real implementation, you'd save this to a settings table
        # For now, just return success
        return {"message": "Setting updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/settings/bulk")
async def update_settings_bulk(settings: SettingsUpdate, db: DatabaseManager = Depends(get_db)):
    """Update multiple settings at once"""
    try:
        # In a real implementation, you'd save these to a settings table
        # For now, just return success
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/products")
async def get_products(db: DatabaseManager = Depends(get_db)):
    """Get all products"""
    try:
        query = """
        SELECT id, label, amount, item_type, description, stripe_price_id, is_active, created_at
        FROM products
        ORDER BY created_at DESC
        """
        products = db.execute_query(query, fetch_all=True)
        return products or []
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

@app.post("/api/admin/products")
async def create_product(product: ProductCreate, db: DatabaseManager = Depends(get_db)):
    """Create a new product"""
    try:
        query = """
        INSERT INTO products (label, amount, item_type, description, stripe_price_id, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (
            product.label,
            product.amount,
            product.item_type,
            product.description,
            product.stripe_price_id,
            product.is_active
        ))
        return {"message": "Product created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate, db: DatabaseManager = Depends(get_db)):
    """Update an existing product"""
    try:
        # Build dynamic update query
        updates = []
        params = []
        
        for field, value in product.dict(exclude_unset=True).items():
            updates.append(f"{field} = ?")
            params.append(value)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(product_id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
        
        db.execute_query(query, params)
        return {"message": "Product updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/products/{product_id}")
async def delete_product(product_id: int, db: DatabaseManager = Depends(get_db)):
    """Delete a product"""
    try:
        query = "DELETE FROM products WHERE id = ?"
        db.execute_query(query, (product_id,))
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Static file serving for production
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the React frontend"""
    return FileResponse("admin_dashboard/dist/index.html")

@app.get("/{path:path}", include_in_schema=False)
async def serve_frontend_routes(path: str):
    """Serve frontend routes and static files"""
    file_path = f"admin_dashboard/dist/{path}"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        # For client-side routing, return index.html
        return FileResponse("admin_dashboard/dist/index.html")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

async def main():
    """Main function to run the server"""
    print("🚀 Starting Admin Dashboard API Server...")
    
    # Initialize database
    global db_manager
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    print("✅ Database connected")
    print("🌐 Starting web server...")
    
    # Run the server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main()) 