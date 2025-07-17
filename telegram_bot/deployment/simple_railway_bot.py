#!/usr/bin/env python3
"""
Railway Deployment Script
This script is the single entry point for the Railway deployment.
It imports and runs the main bot application, which is configured
to run in webhook mode.
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

# Import the main application entry point
from src import bot as application_bot

# Configure basic logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("🚀 Launching bot in webhook mode for Railway...")
    try:
        # Get the current event loop
        loop = asyncio.get_event_loop()
        # Run the main async function from our refactored bot
        loop.run_until_complete(application_bot.main())
    except Exception as e:
        logger.critical(f"❌ Bot application failed to launch: {e}", exc_info=True)
        # Exit with a non-zero code to signal failure to Railway
        sys.exit(1)