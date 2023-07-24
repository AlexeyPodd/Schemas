from functools import wraps

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from mainapp.models import Schema


def base_view_for_ajax(allowed_method):
    def wrapper(view_func):
        @wraps(view_func)
        def wrapped(request):
            """Necessary checks and getting schema model object."""

            if request.method != allowed_method:
                return JsonResponse({'error': 'Method not allowed'}, status=405)

            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Not Founded'}, status=404)

            schema_slug = request.POST.get('schema') if allowed_method == 'POST' else request.GET.get('schema')
            try:
                schema = Schema.objects.select_related('owner').get(slug=schema_slug, owner=request.user)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Not Founded'}, status=404)

            return view_func(request, schema)
        return wrapped
    return wrapper
