"""
Compatibility settings module.

Some IDE run-configs may point to ``config.settings`` instead of
``config.settings.base``. Keep this module as a thin wrapper so both
entry-points behave the same.
"""

from config.settings.base import *  # noqa: F401,F403
