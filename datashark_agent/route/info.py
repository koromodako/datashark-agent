"""/info route
"""
from aiohttp import web
from datashark_core.model.api import AgentInfoResponse


async def info(_):
    """GET /info implementation"""
    return web.json_response(AgentInfoResponse.build({}).as_dict())


def setup(webapp):
    """Setup routes"""
    webapp.add_routes([
        web.get('/info', info),
    ])
