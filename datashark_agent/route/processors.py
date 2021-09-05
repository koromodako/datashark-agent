"""/processors route
"""
import re
from aiohttp import web
from datashark_core.model.api import ProcessorsRequest, ProcessorsResponse
from datashark_core.meta.processor import enumerate_processor_classes


async def processors(request):
    """POST /processors implementation"""
    proc_req = ProcessorsRequest.build(await request.json())
    search_re = None
    if proc_req.search:
        try:
            search_re = re.compile(proc_req.search)
        except SyntaxError as exc:
            raise web.HTTPBadRequest() from exc
    processor_classes = []
    for processor_class in enumerate_processor_classes():
        if search_re and not search_re.search(processor_class.name()):
            continue
        processor_classes.append(processor_class)
    if not processor_classes:
        raise web.HTTPNotFound()
    proc_resp = ProcessorsResponse(processors=[
        processor_class.processor()
        for processor_class in processor_classes
    ])
    return web.json_response(proc_resp.as_dict())


def setup(webapp):
    """Setup routes"""
    webapp.add_routes([
        web.post('/processors', processors),
    ])
