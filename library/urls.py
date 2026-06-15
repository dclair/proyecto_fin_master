from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('crear/', views.ArticleCreateView.as_view(), name='article_create'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('<slug:slug>/editar/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('<slug:slug>/eliminar/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('<slug:slug>/comentar/', views.add_comment, name='add_comment'),
    path('<slug:slug>/valorar/', views.rate_article, name='rate_article'),
]
