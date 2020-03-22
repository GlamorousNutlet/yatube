from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name = 'index'),
    path('group/<str:slug>', views.group_posts, name="group"),
    # раздел добавления нового поста
    path('new/', views.new_post, name="new_post")
]