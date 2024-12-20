from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )

    class Meta:
        abstract = True


class Location(BaseModel):
    name = models.CharField(
        'Название места',
        max_length=256,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Category(BaseModel):
    title = models.CharField(
        'Заголовок',
        max_length=256,
    )
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        ),
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Post(BaseModel):
    title = models.CharField(
        'Заголовок',
        max_length=256,
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='author',
    )
    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name='location',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        null=True,
        on_delete=models.SET_NULL,
        related_name='category',
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
