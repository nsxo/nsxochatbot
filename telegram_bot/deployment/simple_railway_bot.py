#!/usr/bin/env python3
"""
Railway Deployment Script
This script is the single entry point for the Railway deployment.
It performs pre-flight checks and runs the main bot application.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = str(project_root / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import the main application entry point and health check
from src import bot as application_bot
from src.database import check_database_health

# Configure basic logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Performs startup checks and launches the bot application."""
    logger.info("🔬 Performing pre-flight health checks...")

    # 1. Database Health Check
    db_health = check_database_health()
    if db_health.get('status') != 'healthy':
        logger.critical(f"❌ Database health check failed: {db_health.get('error')}")
        sys.exit(1)
    logger.info("✅ Database health check successful.")

    logger.info("🚀 Launching bot application...")
    await application_bot.main()


if __name__ == '__main__':
    try:
        # Use asyncio.run() as the single entry point to the async world
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"❌ Bot application failed to launch: {e}", exc_info=True)
        # Exit with a non-zero code to signal failure to Railway
        sys.exit(1)