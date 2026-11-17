from django import template
from django.utils.safestring import mark_safe
from aficionados_network.utils.sanitizer import sanitize_html as _sanitize_html

register = template.Library()

@register.filter(name="sanitize_html")
def sanitize_html_filter(value):
    if not value:
        return ""
    return mark_safe(_sanitize_html(value))

