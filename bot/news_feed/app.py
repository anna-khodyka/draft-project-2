
from aiohttp import web
import aiohttp
import os
import asyncio

if __package__ == "" or __package__ is None:
    from settings import urls_dict
    from get_content2 import *
else:
    from .settings import urls_dict
    from .get_content2 import *



async def get_feed(request):
    async with aiohttp.ClientSession() as http_session:
        task_lst = []
        for key in urls_dict.keys():
            task_lst.append(asyncio.create_task(
                get_content(
                            urls_dict[key]['url'],
                            ParserCls=globals()[urls_dict[key]['parser']],
                            session=http_session)))
        feed = await asyncio.gather(*task_lst, loop=None, return_exceptions=False)
        return feed


