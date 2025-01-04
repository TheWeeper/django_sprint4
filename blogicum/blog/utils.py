from django.utils import timezone


def get_published_posts(queryset):
    new_queryset = queryset.filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True,
    )
    return new_queryset
