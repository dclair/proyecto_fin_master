from django import template
from library.models import Article

register = template.Library()

@register.simple_tag
def get_articles_count():
    count = Article.objects.count()
    if count > 999:
        return "+999"
    return str(count)
