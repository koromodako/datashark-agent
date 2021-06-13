"""Datashark Service
"""
from .__version__ import version, version_tuple
from datashark_core.logging import LOGGING_MANAGER

NAME = 'service'
LOGGER = LOGGING_MANAGER.get_logger(NAME)
