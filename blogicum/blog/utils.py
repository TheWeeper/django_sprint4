from django.utils.timezone import now


def get_published_status(queryset):
    new_queryset = queryset.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    )
    return new_queryset
