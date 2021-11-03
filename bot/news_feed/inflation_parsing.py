from html.parser import HTMLParser
import asyncio
from markupsafe import Markup


class InflationHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.title = ''
        self.write_title_data = False
        self.is_save_div = False
        self.body = ''

    async def feed(self, data):
        super().feed(data)

    def write_tag(self, tag, attrs):
        self.body += f'<{tag} '
        for attr in attrs:
            self.body += attr[0] + '=' + attr[1] + ' '
        self.body += '>'

    def handle_starttag(self, tag, attrs):
        look_for_div = 'idx-block-1120-'
        if tag == 'title':
            self.write_title_data = True
        elif tag == 'div':
            if look_for_div in [attr[1] for attr in attrs]:
                self.is_save_div = True
        if self.is_save_div:
            self.write_tag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'title':
            self.write_title_data = False
        elif self.is_save_div:
            if tag == 'div':
                self.is_save_div = False
            self.body += f'</{tag}>'

    def handle_data(self, data):
        if self.write_title_data:
            self.title = data
        if self.is_save_div:
            self.body += data

    async def clear_text(self):
        self.body = Markup(self.body)
