from html.parser import HTMLParser


class LoginFormParser(HTMLParser):
    """
    A lightweight parser to replace BeautifulSoup.
    It extracts the action URL and hidden inputs from the first <form> found.
    """

    def __init__(self):
        super().__init__()
        self.action = None
        self.hidden_inputs = {}
        self._in_target_form = False
        self._found_first_form = False

    def handle_starttag(self, tag, attrs):
        # Stop processing if we already finished parsing the first form
        if self._found_first_form and not self._in_target_form:
            return

        attrs_dict = dict(attrs)

        if tag == 'form':
            self._in_target_form = True
            self._found_first_form = True
            self.action = attrs_dict.get('action')

        elif tag == 'input' and self._in_target_form:
            # Capture hidden inputs specifically
            if attrs_dict.get('type') == 'hidden':
                name = attrs_dict.get('name')
                value = attrs_dict.get('value', '')
                if name:
                    self.hidden_inputs[name] = value

    def handle_endtag(self, tag):
        if tag == 'form' and self._in_target_form:
            self._in_target_form = False