from shame.models import Store

class Subdomain(object):
    def process_request(self, request):
        subdomain = request.META['HTTP_HOST'].split('.')[0]
        try:
            request.store = Store.objects.get(subdomain=subdomain)
        except Store.DoesNotExist:
            request.store = None
        return None
