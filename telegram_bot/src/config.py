#!/usr/bin/env python3
"""
Configuration management for the Telegram Bot, powered by Pydantic.
"""

from typing import Optional, List, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Defines all application settings, loaded from environment variables.
    Utilizes Pydantic for automatic validation and type casting.
    """
    # Load .env file in local development
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # --- Core Bot Configuration ---
    BOT_TOKEN: str
    DATABASE_URL: str
    ADMIN_CHAT_ID: int
    RAILWAY_STATIC_URL: str # The public URL of your Railway service
    TELEGRAM_SECRET_TOKEN: str # A random secret string for webhook security

    # --- Optional & Defaulted Configuration ---
    ADMIN_GROUP_ID: Optional[int] = None
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_PORT: int = int(os.getenv('PORT', '8000'))  # Use Railway's PORT variable if available
    LOG_LEVEL: str = 'INFO'
    REDIS_URL: Optional[str] = None
    SENTRY_DSN: Optional[str] = None

# Create a single, globally accessible instance of the settings
try:
    settings = Settings()
except Exception as e:
    # This will catch validation errors on startup
    print(f"FATAL: Configuration validation failed: {e}")
    exit(1)

# You can still use nested classes for namespacing constants if you like,
# but they are no longer part of the settings loading/validation process.
class BusinessConstants:
    """Business logic configuration constants."""
    DEFAULT_TEXT_COST: int = 1
    DEFAULT_PHOTO_COST: int = 3
    DEFAULT_VOICE_COST: int = 5
    QUICK_BUY_OPTIONS: List[int] = [10, 25, 50, 100]

class PerformanceConstants:
    """Performance configuration constants."""
    SETTINGS_CACHE_TTL: int = 300
    USER_CREDITS_CACHE_TTL: int = 60