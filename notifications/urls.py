from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    # Tu vista de lista (la que es una clase)
    path("", views.NotificationListView.as_view(), name="list"),
    # LA CORRECCIÓN: Quita "NotificationListView." de aquí
    path("read/<int:pk>/", views.notification_redirect, name="notification_redirect"),
    # esta urls es para el contador de notificaciones
    path("api/unread-count/", views.api_unread_count, name="api_unread_count"),
    path(
        "go/<int:notification_id>/", views.read_and_redirect, name="read_and_redirect"
    ),
    path("delete/<int:pk>/", views.delete_notification, name="delete_notification"),
    path("delete-all/", views.delete_all_notifications, name="delete_all_notifications"),
]
