"""Constants for the SmartIf."""

# Integration domain
from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final = "smartif"
LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=10)
