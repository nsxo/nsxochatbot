#!/usr/bin/env python3
"""
Main entry point for the Telegram Bot.
Run this file from the project root to start the bot.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the bot
if __name__ == "__main__":
    from bot import main
    main()