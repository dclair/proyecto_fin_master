# profiles/urls.py
from django.urls import path

from .views import (
    ProfilesListView,
    ProfileView,
    ProfileUpdateView,
    add_hobby,
    delete_hobby,
    add_review,
    upload_image_tinymce,
)

app_name = "profiles"

urlpatterns = [
    path("list/", ProfilesListView.as_view(), name="profile_list"),
    path("<int:pk>/", ProfileView.as_view(), name="profile"),
    path("edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path("hobby/add/", add_hobby, name="add_hobby"),
    path("hobby/delete/<int:hobby_id>/", delete_hobby, name="delete_hobby"),
    path("review/add/<int:event_id>/", add_review, name="add_review"),
    path("upload-image/", upload_image_tinymce, name="upload_image"),
]
