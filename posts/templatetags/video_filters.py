import re
from django import template

register = template.Library()

@register.filter
def video_platform(url):
    """
    Returns the platform name based on the URL.
    Returns 'youtube', 'vimeo', 'twitch', or 'other'.
    """
    if not url:
        return 'other'
    
    if re.search(r'(youtube|youtu|youtube-nocookie)\.(com|be)', url):
        return 'youtube'
    elif re.search(r'vimeo\.com', url):
        return 'vimeo'
    elif re.search(r'twitch\.tv', url):
        return 'twitch'
    
    return 'other'

@register.filter
def youtube_embed(url):
    if not url:
        return url
        
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    match = re.search(youtube_regex, url)
    if match:
        video_id = match.group(6)
        return f"https://www.youtube-nocookie.com/embed/{video_id}"
    
    return url

@register.filter
def vimeo_embed(url):
    if not url:
        return url
        
    vimeo_regex = r'(https?://)?(www\.)?vimeo\.com/(\d+)'
    match = re.search(vimeo_regex, url)
    if match:
        video_id = match.group(3)
        return f"https://player.vimeo.com/video/{video_id}"
        
    return url

@register.filter
def twitch_embed(url, host="localhost"):
    if not url:
        return url
        
    domain = host.split(':')[0] if host else "localhost"
        
    twitch_regex = r'(https?://)?(www\.)?twitch\.tv/([a-zA-Z0-9_]+)'
    match = re.search(twitch_regex, url)
    if match:
        channel_or_videos = match.group(3)
        if channel_or_videos == 'videos':
            video_id_regex = r'twitch\.tv/videos/(\d+)'
            v_match = re.search(video_id_regex, url)
            if v_match:
                return f"https://player.twitch.tv/?video=v{v_match.group(1)}&parent={domain}"
        else:
            return f"https://player.twitch.tv/?channel={channel_or_videos}&parent={domain}"
            
    return url
