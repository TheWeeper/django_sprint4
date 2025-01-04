from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = (
            'is_published',
            'created_at',
            'author',
        )
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
