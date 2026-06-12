from django import template
from marketplace.models import Listing

register = template.Library()

@register.simple_tag
def get_active_listings_count():
    count = Listing.objects.filter(status='AVAILABLE').count()
    if count > 99:
        return "+99"
    return str(count)
