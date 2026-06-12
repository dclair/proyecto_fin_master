from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.ListingListView.as_view(), name='listing_list'),
    path('nuevo/', views.ListingCreateView.as_view(), name='listing_create'),
    path('<slug:slug>/', views.ListingDetailView.as_view(), name='listing_detail'),
    path('<slug:slug>/editar/', views.ListingUpdateView.as_view(), name='listing_update'),
    path('<slug:slug>/eliminar/', views.ListingDeleteView.as_view(), name='listing_delete'),
    path('vendedor/<str:username>/valorar/', views.add_seller_review, name='add_seller_review'),
]
