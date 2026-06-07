import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aficionados_network.settings')
django.setup()

from chat.models import Message
from django.contrib.auth.models import User

try:
    msg = Message.objects.last()
    user = User.objects.first()
    print(f"Adding user {user} to hidden_by of message {msg}")
    msg.hidden_by.add(user)
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
