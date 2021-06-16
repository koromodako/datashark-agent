"""Datashark CLI entry point
"""
import sys
from pathlib import Path
from argparse import ArgumentParser
from aiohttp import web
from aiohttp_basicauth import BasicAuthMiddleware
from ds_core import BANNER
from ds_core.api import Artifact
from ds_core.config import DSConfiguration, DEFAULT_CONFIG_PATH
from ds_core.plugin import load_installed_plugins
from ds_core.logging import LOGGING_MANAGER
from ds_core.dispatcher import (
    DS_PLUGIN_JOBS,
    DS_DISPATCH_JOBS,
    enqueue_dispatch,
)
from . import LOGGER


async def info(request):
    return web.json_response(
        {
            'plugin_job_count': len(DS_PLUGIN_JOBS.job_ids),
            'dispatch_job_count': len(DS_DISPATCH_JOBS.job_ids),
        }
    )


async def process(request):
    data = await request.json()
    obj = Artifact(data['filepath'])
    job = enqueue_dispatch(obj)
    return web.json_response({'job': job.id})


def parse_args():
    parser = ArgumentParser(description="Datashark Service")
    parser.add_argument(
        '--debug', '-d', action='store_true', help="Enable debugging"
    )
    parser.add_argument(
        '--config',
        '-c',
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Configuration file",
    )
    args = parser.parse_args()
    args.config = DSConfiguration(args.config)
    return args


def run(args):
    LOGGING_MANAGER.set_debug(args.debug)
    load_installed_plugins()
    auth = BasicAuthMiddleware(
        username=args.config.get('datashark.service.username', default='user'),
        password=args.config.get('datashark.service.password'),
    )
    webapp = web.Application(middlewares=[auth])
    webapp['config'] = args.config
    webapp.add_routes(
        [
            web.get('/info', info),
            web.post('/process', process),
        ]
    )
    bind = args.config.get('datashark.service.bind', default='127.0.0.1')
    port = args.config.get('datashark.service.port', default=13740)
    LOGGER.info("starting on: %s:%s", bind, port)
    web.run_app(webapp, host=bind, port=port, handle_signals=True)


def app():
    """Application entry point"""
    LOGGER.info(BANNER)
    args = parse_args()
    exitcode = 0
    try:
        run(args)
    except:
        LOGGER.exception("unexpected exception!")
        exitcode = 1
    sys.exit(exitcode)
