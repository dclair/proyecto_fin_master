"""
HTML Sanitizer Utility for Aficionados Network.
Protects rich-text fields (TinyMCE inputs) against Stored XSS.
Uses `nh3` if installed, falling back to `BeautifulSoup4`.
"""

import os

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

    # Fallback to BeautifulSoup4
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
    except Exception:
        # Ultimate fallback if parsing fails: escape HTML
        import html
        return html.escape(html_content)

