from django.utils import timezone
from django.http import Http404
from django.shortcuts import render, get_object_or_404


from .models import Category, Post
from .utils import get_published_status


# Create your views here.
def index(request):
    template_name = 'blog/index.html'
    today = timezone.now()
    post_list = get_published_status(Post, today)[:5]
    context = {'post_list': post_list}
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(Post, pk=post_id)
    today = timezone.now()
    if today < post.pub_date or not (post.is_published
                                     and post.category.is_published):
        raise Http404()
    context = {'post': post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(Category, slug=category_slug)
    if not category.is_published:
        raise Http404()
    today = timezone.now()
    post_list = get_published_status(Post, today).filter(
        category=category,
    )
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, template_name, context)
