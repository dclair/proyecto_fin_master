"""
Utility functions for site domain and absolute URL resolution across the project.
Supports request-context resolution, django.contrib.sites fallback,
and environment variable overrides (SITE_DOMAIN, SITE_URL).
"""
import logging
from urllib.parse import urlparse
from django.conf import settings

logger = logging.getLogger(__name__)


def get_site_domain():
    """
    Returns the configured or current site domain without protocol or trailing slash.
    Resolution priority:
    1. settings.SITE_DOMAIN
    2. Derived from settings.SITE_URL (e.g. 'https://example.com' -> 'example.com')
    3. django.contrib.sites.models.Site (if not 'example.com')
    4. First non-wildcard, non-local entry from settings.ALLOWED_HOSTS
    5. Fallback: 'localhost:8000'
    """
    site_domain = getattr(settings, "SITE_DOMAIN", "")
    if site_domain:
        return site_domain.strip().rstrip("/")

    site_url = getattr(settings, "SITE_URL", "")
    if site_url:
        parsed = urlparse(site_url if "://" in site_url else f"http://{site_url}")
        if parsed.netloc:
            return parsed.netloc

    try:
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        if current_site.domain and current_site.domain != "example.com":
            return current_site.domain
    except Exception:
        pass

    allowed = getattr(settings, "ALLOWED_HOSTS", [])
    for host in allowed:
        host = host.strip()
        if host and host not in ("*", "localhost", "127.0.0.1", "testserver"):
            return host

    return "localhost:8000"


def get_site_protocol():
    """
    Returns 'https' or 'http' based on settings.
    """
    site_url = getattr(settings, "SITE_URL", "")
    if site_url.startswith("https://"):
        return "https"
    protocol = getattr(settings, "SITE_PROTOCOL", "")
    if protocol:
        return protocol
    if getattr(settings, "SECURE_SSL_REDIRECT", False):
        return "https"
    return "http"


def get_base_url(request=None):
    """
    Returns the absolute base URL (e.g., 'https://hubsclicks.com' or 'http://141.148.227.48')
    without a trailing slash.
    """
    if request:
        try:
            return request.build_absolute_uri("/").rstrip("/")
        except Exception:
            pass

    site_url = getattr(settings, "SITE_URL", "")
    if site_url:
        return site_url.strip().rstrip("/")

    domain = get_site_domain()
    protocol = get_site_protocol()
    return f"{protocol}://{domain}"


def build_absolute_url(path, request=None):
    """
    Ensures a path or URL is absolute. If it already starts with http:// or https://,
    returns it unchanged. Otherwise prefixes it with get_base_url(request).
    """
    if not path:
        return get_base_url(request)
    if path.startswith("http://") or path.startswith("https://"):
        return path
    base = get_base_url(request)
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{base}{path}"
