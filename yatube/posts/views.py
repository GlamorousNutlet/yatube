from django.shortcuts import render, redirect
from .models import Post, Group, User
from .forms import PostForm
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.

    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})

def new_post(request):
    user = request.user
    form = PostForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def profile(request, username):
    # тут тело функции
    profile = User.objects.get(username=username)
    posts = Post.objects.filter(author=profile).order_by('-pub_date').all()
    posts_count = posts.count()
    return render(request, "profile.html", {"posts":posts, "profile" : profile, "posts_count" : posts_count})

def post_view(request, username, post_id):
    # тут тело функции
    profile = get_object_or_404(User, username=username)
    post = Post.objects.get(author=profile.pk, id=post_id)
    posts = Post.objects.filter(author = profile).order_by('-pub_date').all()
    posts_count = posts.count()
    return render(request, "post.html", {"profile":profile, 'post':post, "posts_count":posts_count,})

def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return HttpResponse("Вы не можете редактировать чужую запись!")
    if request.method == 'GET':
        form = PostForm(instance=post)
        return render(request, "new_post.html", {"form": form, 'edit': True})
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            group = form.cleaned_data['group']
            text = form.cleaned_data['text']
            post.group = group
            post.text = text
            post.save()
            return redirect(reverse('index'))
    return render(request, "new_post.html", {"form": form, 'edit': True})
