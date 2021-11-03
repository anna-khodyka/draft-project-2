from html.parser import HTMLParser
import asyncio
import re
from markupsafe import Markup


class CovidHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.title = ''
        self.start_text_pos = 0
        self.end_text_pos = 0
        self.write_title_data = False
        self.is_editor_div = False
        self.body = ''

    async def feed(self, data):
        super().feed(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.write_title_data = True
        elif tag == 'div':
            if 'editor' in [attr[1] for attr in attrs]:
                self.is_editor_div = True
                return None
        if tag == 'table' and self.is_editor_div:
            self.is_editor_div = False

    def handle_endtag(self, tag):
        if tag == 'title':
            self.write_title_data = False

    def handle_data(self, data):
        if self.write_title_data:
            self.title = data
        if self.is_editor_div:
            self.body += data

    async def clear_text(self):
        self.body = re.sub("(?P<digits>\ [\d]+)", '<b>\g<digits></b>', self.body)
        self.body = Markup(self.body)
