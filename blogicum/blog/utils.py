def get_published_status(Queryset, today):
    new_Queryset = Queryset.objects.select_related(
        'category'
    ).filter(
        is_published=True,
        pub_date__lt=today,
        category__is_published=True,
    )
    return new_Queryset
