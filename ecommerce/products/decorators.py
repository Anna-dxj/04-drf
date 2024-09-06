from django.http import HttpResponseForbidden

def vendor_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request.user.customer, 'is_vendor', False):
            return HttpResponseForbidden('You must be a vendor to access this page!')
        return view_func(request, *args, **kwargs)
    return _wrapped_view