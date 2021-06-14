"""Datashark CLI entry point
"""
import sys
from argparse import ArgumentParser
from aiohttp import web
from aiohttp_basicauth import BasicAuthMiddleware
from ds_core import BANNER
from ds_core.api import Artifact
from ds_core.config import CONFIG
from ds_core.plugin import load_installed_plugins
from ds_core.logging import LOGGING_MANAGER
from ds_core.dispatcher import (
    DS_PLUGIN_JOBS,
    DS_DISPATCH_JOBS,
    enqueue_dispatch,
)
from . import LOGGER


async def info(request):
    return web.json_response({
        'plugin_job_count': len(DS_PLUGIN_JOBS.job_ids),
        'dispatch_job_count': len(DS_DISPATCH_JOBS.job_ids),
    })


async def process(request):
    data = await request.json()
    obj = Artifact(data['filepath'])
    job = enqueue_dispatch(obj)
    return web.json_response({'job': job.id})


def parse_args():
    parser = ArgumentParser(description="Datashark Service")
    parser.add_argument('--debug', '-d', action='store_true')
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
    LOGGING_MANAGER.set_debug(args.debug)
    load_installed_plugins()
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
