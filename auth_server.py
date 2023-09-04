#! --*-- coding: utf-8 --*--

import asyncio

from aiohttp import web

async def index(request):
    print(request.headers)
    resp = web.Response(body=b'<h1>Index</h1>')
    resp.headers['Auth-Status'] = 'OK'
    resp.headers['Auth-Server'] = 'mail5.example.com'
    resp.headers['Auth-Port'] = '25'
    print(resp.headers)
    return resp

async def hello(request):
    await asyncio.sleep(0.5)
    text = '<h1>hello, %s!</h1>' % request.match_info['name']
    return web.Response(body=text.encode('utf-8'))

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/auth', index)
    srv = await loop.create_server(app.make_handler(), '0.0.0.0', 6000)
    print('Server started at http://0.0.0.0:6000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()