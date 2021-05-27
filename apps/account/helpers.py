from rest_framework.exceptions import NotFound


def get_object_or_404(klass, *args, **kwargs):
    """
    By analogy with django.shortcuts.get_object_or_404,
    but with using djangorestframework's NotFound exception
    instead of django Http404
    """
    queryset = klass
    if hasattr(klass, '_default_manager'):
        queryset = klass._default_manager.all()

    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise NotFound()
