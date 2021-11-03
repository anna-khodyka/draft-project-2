from html.parser import HTMLParser
from markupsafe import Markup

class CurrencyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.title = ''
        self.start_text_pos = 0
        self.end_text_pos = 0
        self.write_title_data = False
        self.is_save_table = False
        self.body=''
        self.skip_span = False

    async def feed(self, data):
        super().feed(data)

    def write_tag(self, tag, attrs):
        if tag =='a':
            pass
        elif self.skip_span:
            pass
        else:
            self.body += f'<{tag} '
            for attr in attrs:
                self.body += attr[0] + '=' + attr[1] + ' '
            self.body += ('>')


    def handle_starttag(self, tag, attrs):
        look_for_table= 'table-response mfm-table mfcur-table-lg mfcur-table-lg-currency has-no-tfoot'
        skip_span = [
                     'mfm-tooltip-body',
                     'mfm-text-light-grey mfm-posr',
                     'mfm-hover-show mfm-table-trend icon-down-open',
                     'mfm-hover-show mfm-table-trend icon-up-open',
                     'mfm-text-grey',
                     'mfcur-nbu-full mfm-text-grey mfm-text-nowrap mfm-hover-show icon-down-open',
                     'mfm-hover-show mfm-table-trend icon-open',
                     'mfcur-nbu-full mfm-text-grey mfm-text-nowrap mfm-hover-show icon-up-open',
                     ]
        if tag == 'title':
            self.write_title_data = True
        elif tag == 'table':
            if look_for_table in [attr[1] for attr in attrs]:
                self.is_save_table = True
        elif tag == 'span':
            for span in skip_span:
                if span in [attr[1] for attr in attrs]:
                    self.skip_span = True
        if self.is_save_table and not self.skip_span:
            self.write_tag(tag, attrs)


    def handle_endtag(self, tag):
        if tag == 'title':
            self.write_title_data = False
        elif tag == 'span' and self.skip_span:
            self.skip_span = False
            return
        elif self.is_save_table and not self.skip_span:
            if tag == 'table':
                self.body += f'</{tag}>'
                self.is_save_table = False
            elif tag != 'a':
                self.body += f'</{tag}>'

    def handle_data(self, data):
        if self.write_title_data:
            self.title = data
        if self.is_save_table and not self.skip_span:
            self.body += data

    async def clear_text(self):
        self.body = Markup(self.body)
