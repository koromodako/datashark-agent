"""Datashark CLI entry point
"""
import ssl
from pathlib import Path
from getpass import getpass
from argparse import ArgumentParser
from aiohttp import web
from datashark_core import BANNER
from datashark_core.meta import load_processors
from datashark_core.config import DatasharkConfiguration, override_arg
from datashark_core.logging import LOGGING_MANAGER
from . import LOGGER
from .route import setup as setup_routes


def parse_args():
    parser = ArgumentParser(description="Datashark Service")
    parser.add_argument(
        '--debug', '-d', action='store_true', help="Enable debugging"
    )
    parser.add_argument(
        '--config',
        '-c',
        type=DatasharkConfiguration,
        help="Configuration file",
    )
    parser.add_argument('--bind', '-b', help="Address to listen on")
    parser.add_argument('--port', '-p', type=int, help="Port to listen on")
    parser.add_argument('--ca', help="Clients CA certificate")
    parser.add_argument('--key', help="Server private key")
    parser.add_argument('--cert', help="Server certificate")
    parser.add_argument(
        '--ask-pass',
        action='store_true',
        help="Ask for server private key password",
    )
    args = parser.parse_args()
    args.bind = override_arg(
        args.bind, args.config, 'datashark.agent.bind', default='127.0.0.1'
    )
    args.port = override_arg(
        args.port, args.config, 'datashark.agent.port', default=13740
    )
    args.ca = Path(override_arg(
        args.ca,
        args.config,
        'datashark.agent.ca',
        input("Enter CLI CA certificate path: ")
    ))
    if not args.ca.is_file():
        LOGGER.error("You must provide a valid CLI CA certificate path!")
        return None
    args.key = Path(override_arg(
        args.key,
        args.config,
        'datashark.agent.key',
        input("Enter agent key path: ")
    ))
    if not args.key.is_file():
        LOGGER.error("You must provide a valid agent private key path!")
        return None
    args.cert = Path(override_arg(
        args.cert,
        args.config,
        'datashark.agent.cert',
        input("Enter agent cert path: ")
    ))
    if not args.cert.is_file():
        LOGGER.error("You must provide a valid agent certificate path!")
        return None
    return args


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
    # create web application instance
    webapp = web.Application()
    # set webapp variables
    webapp['config'] = args.config
    # setup web application route handlers
    setup_routes(webapp)
    # create ssl context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # enforce client certificate validation
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    # load server certificate
    password = None
    if args.ask_pass:
        password = getpass("Enter client private key password: ")
    ssl_context.load_cert_chain(
        certfile=str(args.cert),
        keyfile=str(args.key),
        password=password,
    )
    # load clients CA certificate
    ssl_context.load_verify_locations(cafile=str(args.ca))
    # run webapp
    LOGGER.info("starting on: %s:%s", args.bind, args.port)
    web.run_app(
        webapp,
        host=args.bind,
        port=args.port,
        ssl_context=ssl_context,
        handle_signals=True,
    )
