"""Datashark CLI entry point
"""
import sys
from argparse import ArgumentParser
from aiohttp import web
from aiohttp_basicauth import BasicAuthMiddleware
from datashark_core import BANNER
from datashark_core.config import CONFIG
from . import LOGGER


async def info(request):
    return web.json_response({})


async def process(request):
    return web.json_response({})


def parse_args():
    parser = ArgumentParser(description="Datashark Service")
    parser.add_argument(
        '--bind',
        default=CONFIG.get_('datashark', 'service', 'bind', default='127.0.0.1'),
    )
    parser.add_argument(
        '--port',
        default=CONFIG.get_('datashark', 'service', 'port', default=13740),
    )
    parser.add_argument(
        '--user',
        default=CONFIG.get_('datashark', 'service', 'user', default='user'),
    )
    parser.add_argument(
        '--pswd',
        default=CONFIG.get_('datashark', 'service', 'pswd'),
    )
    return parser.parse_args()


def app():
    """Application entry point"""
    LOGGER.info(BANNER)
    args = parse_args()
    auth = BasicAuthMiddleware(username=args.user, password=args.pswd)
    webapp = web.Application(middlewares=[auth])
    webapp.add_routes([
        web.get('/info', info),
        web.post('/process', process),
    ])
    LOGGER.info("starting on: %s:%s", args.bind, args.port)
    exitcode = 0
    try:
        web.run_app(
            webapp,
            host=args.bind,
            port=args.port,
            handle_signals=True,
        )
    except:
        LOGGER.exception("unexpected exception!")
        exitcode = 1
    sys.exit(exitcode)
