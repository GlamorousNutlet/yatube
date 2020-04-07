from django.shortcuts import render, redirect
from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)

def server_error(request):
    return render(request, "misc/500.html", status=500)

def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.

    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "group.html", {"group": group, "page": page, "paginator": paginator})

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def profile(request, username):
    # тут тело функции
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).order_by('-pub_date').all()
    posts_count = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "profile.html", {"posts":posts, "profile" : profile, "posts_count" : posts_count, "paginator": paginator,  "page": page})

def post_view(request, username, post_id):
    # тут тело функции
    profile = get_object_or_404(User, username=username)
    post = Post.objects.get(author=profile.pk, id=post_id)
    posts = Post.objects.filter(author = profile).order_by('-pub_date').all()
    posts_count = posts.count()
    items = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    return render(request, "post.html", {"profile":profile, 'post':post, "posts_count":posts_count, "form": form, "items": items, 'username': username})

def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("post", username=post.author, post_id=post.pk)
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post", username=post.author, post_id=post.pk)
    else:
        form = PostForm(instance=post)
        return render(request, "new_post.html", {"form": form, 'edit': True, "post": post})
    return render(request, "new_post.html", {"form": form, 'edit': True, "post":post})

def add_comment(request, post_id, username):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    items = Comment.objects.filter(post_id=post_id)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
    return redirect("post", username, post_id)



