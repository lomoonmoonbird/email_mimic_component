#! --*-- coding: utf-8 --*--
import asyncio
from aiohttp import web, ClientSession
import json
from copy import copy

async def proxy(request):
    match_info = request.match_info

    urls = ["http://mail2.moonmoonbird.com"]
    tasks = []
    for url in urls:
        tasks.append(asyncio.Task(worker(request, url)))
    results = await asyncio.gather(*tasks)
    # print(results)
    response_headers = results[0][1]
    import multidict
    response_headers = multidict.CIMultiDict(response_headers)
    if 'Transfer-Encoding' in response_headers:
        del response_headers['Transfer-Encoding']
    print(request.path, '===========', response_headers)
    return web.Response(body=results[0][2], headers=response_headers, status=results[0][0])

async def worker(request, url):
    headers = request.headers
    method = request.method
    body = await request.post()
    path = request.path
    query_string = request.rel_url.query

    # url += '/src/'
    url += path

    print(url,method, headers)
    # print(request.__dict__)
    if method == 'POST':
        async with ClientSession(headers=headers) as session:
            async with session.post(url, data=body) as response:
                status = response.status
                response_headers = response.headers
                response_data = await response.read()
                # print(status, response_data, 'post')
                # print(url, headers, body)
                return (status, response_headers, response_data)
    elif method == 'GET':
        async with ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                status = response.status
                response_headers = response.headers
                print(1111)
                response_data = await response.read()
                # print(response_data, 'get')
                return (status, response_headers, response_data)
    else:
        return (500, '', '')



async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('*', '/{tail:.*}', proxy)
    srv = await loop.create_server(app.make_handler(), '0.0.0.0', 8888)
    print('Server started at http://127.0.0.1:8000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()