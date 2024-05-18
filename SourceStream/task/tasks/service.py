from ... import SourceStream;
from . import repackPackages;

from aiohttp import web
import threading
import time

async def handle(request):

    SourceStream.PACKAGES_ALL = True

    if(SourceStream.PACKAGE_REBUILDING):
        SourceStream.PACKAGE_REBUILD_AFTEER_BUILD = True;
    else:
        threading.Thread(target=repackPackages.run).start()

    return web.Response(text="{}")


def run():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    web.run_app(app)