"""/process route
"""
from aiohttp import web
from datashark_core.model.api import ProcessingRequest, ProcessingResponse
from datashark_core.meta.processor import get_processor_class


async def process(request):
    """POST /process implementation"""
    proc_req = ProcessingRequest.build(await request.json())
    processor_class = get_processor_class(proc_req.processor.name)
    if not processor_class:
        raise web.HTTPNotFound()
    webapp = request.app
    processor_instance = processor_class(webapp['config'], webapp['engine'])
    result = await processor_instance.run(proc_req.processor.arguments)
    proc_resp = ProcessingResponse(result=result)
    return web.json_response(proc_resp.as_dict())


def setup(webapp):
    """Setup routes"""
    webapp.add_routes([
        web.post('/process', process),
    ])
