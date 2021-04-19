from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@cache_page(20)
def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {
            'page': page,
            'paginator': paginator,
            'group': group,
        }
    )


@login_required()
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user1 = request.user
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = user1.is_authenticated and Follow.objects.filter(
        user=user1,
        author=author
    ).exists()
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'paginator': paginator,
        'following': following,
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request,
        'post.html',
        {
            'author': post.author,
            'post': post,
            'comments': comments,
            'form': form
        }
    )


@login_required()
def add_comment(request, post_id, username):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = Post.objects.get(
            id=post_id,
            author__username=username
        )
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(
        request,
        'include/comments.html',
        {'form': form, 'post': post}
    )


@login_required()
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != user:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post',
                        username,
                        post_id
                        )
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required()
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html',
        {'page': page, 'paginator': paginator})


@login_required()
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user1 = request.user
    following = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if (not following) and author != user1:
        Follow.objects.create(author=author, user=user1)
    return redirect('profile', username)


@login_required()
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.get(author=author, user=request.user)
    follower.delete()
    return redirect('profile', username)
