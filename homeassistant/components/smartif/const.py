"""Constants for the SmartIf."""

# Integration domain
from datetime import timedelta
import logging
from logging import Logger
from typing import Final

DOMAIN: Final = "smartif"
LOGGER: Logger = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=10)
UPDATE_EVENT: Final = DOMAIN + "_entity_update"
INITIAL_CONNECTION_RETRIES: Final = 10
