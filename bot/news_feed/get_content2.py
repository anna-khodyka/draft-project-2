from datetime import date
if __package__ == "" or __package__ is None:
    from covid_parsing import *
    from currency_parsing import *
    from inflation_parsing import *
else:
    from .covid_parsing import *
    from .currency_parsing import *
    from .inflation_parsing import *


class ContentBlock:

    def __init__(self):
        self.date = date.today()
        self.header = ''
        self.body = ''


async def get_response(url, session):
    try:
        print(f'Start loading URl {url}')
        async with session.get(url) as response:
            assert response.status == 200
            resp = await response.text()
            print(f'Finish loading URl {url}')
            return resp
    except TimeoutError:
        return None


async def get_content(url, ParserCls=None, session=None):
    try:
        source = await get_response(url, session)
        feed_ = await html_parser(source, url, ParserCls)
    except Exception as e:
        feed_ = await error_parser(e)
    return feed_


async def error_parser(source):
    content = ContentBlock()
    content.header = 'Error when preparing content for feed'
    content.body = str(source)
    return content


async def html_parser(source, url, ParserCls):
    print(f'Start parsing URl {url}')
    content = ContentBlock()
    parser = ParserCls()
    await parser.feed(source)
    content.header = parser.title
    content.url = str(url)
    await parser.clear_text()
    content.body = parser.body
    print(f'Finish parsing URl {url}')
    return content
