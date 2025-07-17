"""
Telegram Bot Source Package
Core modules for the premium messaging bot.
"""

import os

__version__ = "1.0.0"

# Read version from VERSION file if available
_version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION')
if os.path.exists(_version_file):
    with open(_version_file, 'r') as f:
        __version__ = f.read().strip()

__all__ = ['__version__']