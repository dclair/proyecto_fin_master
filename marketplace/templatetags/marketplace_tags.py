from django import template
from marketplace.models import Listing

register = template.Library()

@register.simple_tag
def get_active_listings_count():
    count = Listing.objects.filter(status='AVAILABLE').count()
    if count > 999:
        return "+999"
    return str(count)
