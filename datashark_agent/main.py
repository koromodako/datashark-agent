"""Datashark CLI entry point
"""
import ssl
from pathlib import Path
from getpass import getpass
from argparse import ArgumentParser
from functools import partial
from aiohttp import web
from datashark_core import BANNER
from datashark_core.meta import load_processors
from datashark_core.config import DatasharkConfiguration, override_arg
from datashark_core.logging import LOGGING_MANAGER
from datashark_core.filesystem import get_workdir
from datashark_core.model.database import (
    init_database_model,
    init_database_engine,
)
from . import LOGGER
from .route import setup as setup_routes


def parse_args():
    parser = ArgumentParser(description="Datashark Service")
    parser.add_argument(
        '--debug', '-d', action='store_true', help="Enable debugging"
    )
    parser.add_argument('--bind', '-b', help="Address to listen on")
    parser.add_argument('--port', '-p', type=int, help="Port to listen on")
    parser.add_argument('--ca', help="Clients CA certificate")
    parser.add_argument('--key', help="Server private key")
    parser.add_argument('--cert', help="Server certificate")
    parser.add_argument(
        'config', type=DatasharkConfiguration, help="Configuration file"
    )
    args = parser.parse_args()
    args.bind = override_arg(
        args.bind, args.config, 'datashark.agent.bind', default='127.0.0.1'
    )
    args.port = override_arg(
        args.port, args.config, 'datashark.agent.port', default=13740
    )
    args.ca = override_arg(args.ca, args.config, 'datashark.agent.ca')
    if args.ca:
        args.ca = Path(args.ca)
    args.key = override_arg(args.key, args.config, 'datashark.agent.key')
    if args.key:
        args.key = Path(args.key)
    args.cert = override_arg(args.cert, args.config, 'datashark.agent.cert')
    if args.cert:
        args.cert = Path(args.cert)
    return args


def prepare_ssl_context(args):
    """Prepare SSL context"""
    if not args.ca or not args.key or not args.cert:
        return None
    LOGGER.info("preparing SSL context...")
    # create ssl context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # enforce client certificate validation
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    # load server certificate
    ssl_context.load_cert_chain(
        certfile=str(args.cert),
        keyfile=str(args.key),
        password=partial(getpass, "Enter private key password: "),
    )
    # load clients CA certificate
    ssl_context.load_verify_locations(cafile=str(args.ca))
    return ssl_context


def app():
    """Application entry point"""
    LOGGER.info(BANNER)
    args = parse_args()
    LOGGING_MANAGER.set_debug(args.debug)
    LOGGER.debug("command line arguments: %s", args)
    # load processors
    LOGGER.info("loading processors...")
    if not load_processors():
        return
    # initialize database
    engine = init_database_engine(args.config)
    if not init_database_model(engine):
        return
    # create web application instance
    webapp = web.Application()
    # set webapp variables
    webapp['config'] = args.config
    webapp['engine'] = engine
    # setup web application route handlers
    setup_routes(webapp)
    # prepare ssl context if needed
    ssl_context = prepare_ssl_context(args)
    # check workdir
    try:
        LOGGER.info("working directory: %s", get_workdir(args.config))
    except ValueError as exc:
        LOGGER.critical(str(exc))
        return
    # run webapp
    LOGGER.info("starting on: %s:%s", args.bind, args.port)
    web.run_app(
        webapp,
        host=args.bind,
        port=args.port,
        ssl_context=ssl_context,
        handle_signals=True,
    )
