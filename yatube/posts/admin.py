from django.contrib import admin
# из файла models импортируем модель Post
from .models import Post, Group, Comment, Follow

class PostAdmin(admin.ModelAdmin):
    list_display = ("pk","text", "pub_date", "author") # перечислили поля, которые должны отображаться в админке
    search_fields = ("text",) # добавили возможность поиска по тексту постов
    list_filter = ("pub_date",) # добавляем возможность ФИЛЬТРОВАТЬ по дате
    empty_value_display = '-пусто-' # свойство, которое запишет в любое колонку пусто, если там пустота

admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Follow)