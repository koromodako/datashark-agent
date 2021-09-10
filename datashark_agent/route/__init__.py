"""Datashark agent routes
"""
from .info import setup as setup_info
from .process import setup as setup_process
from .processors import setup as setup_processors


def setup(webapp):
    setup_info(webapp)
    setup_process(webapp)
    setup_processors(webapp)
