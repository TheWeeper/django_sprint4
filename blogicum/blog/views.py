from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (
    CreateView, DetailView, DeleteView, ListView, UpdateView
)


from .forms import CommentForm, ProfileForm, PostForm
from .models import Category, Comment, Post
from .utils import get_published_posts

User = get_user_model()


# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10

    def get_queryset(self):
        return get_published_posts(self.model.objects)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(
            self.model.objects.select_related('category', 'location'),
            pk=self.kwargs['post_id'],
        )
        if self.request.user == post.author:
            return post
        published_posts = get_object_or_404(
            get_published_posts(
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


class ProfileRedirectionMixin(LoginRequiredMixin):

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostCreateView(ProfileRedirectionMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostRedirectionMixin(LoginRequiredMixin):
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class AuthorRequiredMixin(LoginRequiredMixin):

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)


class PostUpdateView(PostRedirectionMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(self.model, id=self.kwargs['post_id'])
        if request.user != post.author:
            return redirect(
                reverse(
                    'blog:post_detail',
                    kwargs={'post_id': kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(AuthorRequiredMixin, ProfileRedirectionMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.form_class(instance=self.object)
        # Добавляем форму в контекст для отображения в шаблоне.
        context['form'] = form
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'category'
    slug_url_kwarg = 'category_slug'

    def get_object(self):
        return get_object_or_404(
            self.model.objects,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = get_published_posts(self.object.category.all())
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
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


class ProfileUpdateView(ProfileRedirectionMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user


class CommentCreateView(PostRedirectionMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        post = get_object_or_404(
            Post.objects.select_related('category', 'location'),
            pk=self.kwargs['post_id']
        )
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentMixin(AuthorRequiredMixin, PostRedirectionMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    pass
