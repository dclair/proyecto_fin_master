"""
HTML Sanitizer Utility for Aficionados Network.
Protects rich-text fields (TinyMCE inputs) against Stored XSS.
Uses `nh3` if installed, falls back to `BeautifulSoup4`, and provides a 
zero-dependency standard-library fallback based on `html.parser.HTMLParser`.
"""

import html
import os
from html.parser import HTMLParser

ALLOWED_TAGS = {
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'strike',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
    'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'span', 'div', 'hr', 'sub', 'sup'
}

ALLOWED_ATTRIBUTES = {
    'a': {'href', 'title', 'target', 'rel'},
    'img': {'src', 'alt', 'title', 'width', 'height', 'style', 'class'},
    '*': {'class', 'style'}
}


class _StdlibHTMLSanitizer(HTMLParser):
    VOID_TAGS = {'br', 'hr', 'img', 'input', 'meta', 'link'}
    DROP_CONTENT_TAGS = {'script', 'style', 'iframe', 'object', 'embed', 'applet', 'noscript', 'canvas'}

    def __init__(self, allowed_tags, allowed_attributes):
        super().__init__(convert_charrefs=False)
        self.allowed_tags = allowed_tags
        self.allowed_attributes = allowed_attributes
        self.result = []
        self.drop_depth = 0

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower in self.DROP_CONTENT_TAGS:
            self.drop_depth += 1
            return
        if self.drop_depth > 0:
            return

        if tag_lower in self.allowed_tags:
            tag_allowed_attrs = self.allowed_attributes.get(tag_lower, set()) | self.allowed_attributes.get('*', set())
            sanitized_attrs = []
            is_a_tag = (tag_lower == 'a')
            has_rel = False

            for attr_name, attr_val in attrs:
                attr_name_lower = attr_name.lower()
                if attr_name_lower.startswith('on') or attr_name_lower not in tag_allowed_attrs:
                    continue
                if attr_val is None:
                    attr_val = ''
                if attr_name_lower in ('href', 'src'):
                    val_lower = attr_val.strip().lower()
                    if val_lower.startswith(('javascript:', 'vbscript:', 'data:text/html')):
                        continue
                if is_a_tag and attr_name_lower == 'rel':
                    has_rel = True
                    sanitized_attrs.append(('rel', 'noopener noreferrer'))
                    continue
                sanitized_attrs.append((attr_name_lower, attr_val))

            if is_a_tag and not has_rel:
                sanitized_attrs.append(('rel', 'noopener noreferrer'))

            attrs_str = ''
            if sanitized_attrs:
                attrs_str = ' ' + ' '.join(f'{k}="{html.escape(v, quote=True)}"' for k, v in sanitized_attrs)

            self.result.append(f'<{tag_lower}{attrs_str}>')

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.DROP_CONTENT_TAGS:
            if self.drop_depth > 0:
                self.drop_depth -= 1
            return
        if self.drop_depth > 0:
            return

        if tag_lower in self.allowed_tags and tag_lower not in self.VOID_TAGS:
            self.result.append(f'</{tag_lower}>')

    def handle_data(self, data):
        if self.drop_depth == 0:
            self.result.append(data)

    def handle_entityref(self, name):
        if self.drop_depth == 0:
            self.result.append(f'&{name};')

    def handle_charref(self, name):
        if self.drop_depth == 0:
            self.result.append(f'&#{name};')

    def get_html(self):
        return ''.join(self.result)


def sanitize_html(html_content: str) -> str:
    """
    Sanitizes raw HTML content, removing script, iframe, dangerous attributes
    like onload/onerror, and javascript: protocols.
    """
    if not html_content:
        return ""

    try:
        import nh3
        return nh3.clean(
            html_content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            url_schemes={'http', 'https', 'mailto', 'tel'},
            link_rel='noopener noreferrer'
        )
    except ImportError:
        pass

    # Fallback to BeautifulSoup4 if available
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove disallowed tags and dangerous elements entirely
        for tag in soup.find_all(True):
            tag_name = tag.name.lower()
            if tag_name not in ALLOWED_TAGS:
                tag.decompose()
            else:
                tag_allowed = ALLOWED_ATTRIBUTES.get(tag_name, set()) | ALLOWED_ATTRIBUTES.get('*', set())
                attrs = dict(tag.attrs)
                for attr_name, attr_val in attrs.items():
                    attr_lower = attr_name.lower()
                    if attr_lower not in tag_allowed or attr_lower.startswith('on'):
                        del tag[attr_name]
                    elif attr_lower in ('href', 'src'):
                        val = str(attr_val).strip().lower()
                        if val.startswith(('javascript:', 'vbscript:', 'data:text/html')):
                            del tag[attr_name]

                if tag_name == 'a':
                    tag['rel'] = 'noopener noreferrer'

        return str(soup)
    except ImportError:
        pass

    # Pure Python stdlib fallback
    try:
        parser = _StdlibHTMLSanitizer(ALLOWED_TAGS, ALLOWED_ATTRIBUTES)
        parser.feed(html_content)
        parser.close()
        return parser.get_html()
    except Exception:
        # Ultimate fallback if parsing fails: escape HTML
        return html.escape(html_content)


