from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name = 'index'),
    path('group/<str:slug>', views.group_posts, name="group"),
    # раздел добавления нового поста
    path('new/', views.new_post, name="new_post"),
    # Главная страница
    path("", views.index, name="index"),
    # Профайл пользователя
    path("<username>/", views.profile, name="profile"),
    # Просмотр записи
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    # Добавление коммента
    path("<username>/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("<username>/<int:post_id>/edit", views.post_edit, name="post_edit"),
]