# -- * -- coding:utf-8 --*--

import asyncio
import logging
logging.basicConfig(level=logging.INFO)
from aiohttp import web
from proxies.http_proxy import Proxy

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('POST', '/', Proxy.send_mail)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 9000)
    logging.info('server started at localhost 9000...')
    await site.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()