from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import (
    CreateView, DetailView, DeleteView, ListView, UpdateView
)


from .forms import CommentForm, ProfileForm, PostForm
from .models import Category, Comment, Post
from .utils import get_published_status

User = get_user_model()


# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10

    def get_queryset(self):
        return get_published_status(self.model.objects)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            get_published_status(
                self.model.objects.select_related('category', 'location')
            ),
            pk=self.kwargs['post_id'],
        )
        if self.request.user == post.author:
            return post
        published_posts = get_object_or_404(
            get_published_status(
                self.model.objects.select_related('category', 'location')
            ),
            pk=self.kwargs['post_id'],
        )
        return published_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryPostListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = 10
    context_object_name = 'post_list'

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        post_list = get_published_status(
            Post.objects.select_related('category', 'location')
        ).filter(category=category)
        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return context

class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.object.author.all()
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user},
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(self.model, id=self.kwargs['post_id'])
        request_user = request.user
        author_user = post.author
        if request_user != author_user:
            return redirect(reverse('blog:post_detail', kwargs={'post_id': kwargs['post_id']}))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.form_class(instance=self.object)
        # Добавляем форму в контекст для отображения в шаблоне.
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        post = get_object_or_404(Post.objects.select_related('category', 'location'), id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise Http404()
        return comment

    def get_success_url(self):
        post_field = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': post_field.pk}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        request_user = self.request.user
        if comment.author != request_user and (request_user.is_staff or request_user.is_superuser):
            raise Http404()
        return comment

    def get_success_url(self):
        post_field = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': post_field.pk}
        )
