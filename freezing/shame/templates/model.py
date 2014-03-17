from django.template.base import TemplateDoesNotExist
from django.template.loader import BaseLoader

from shame.models import StoreTemplate

class Loader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        parts = [part for part in template_name.split(';', 1) if len(part)]
        if len(parts) < 2:
            error = 'No store specified'
        else:
            try:
                t = StoreTemplate.objects.get(
                    store__subdomain=parts[0], name=parts[1])
                return (t.content, t)
            except StoreTemplate.DoesNotExist:
                error = 'No {} template for {}'.format(*reversed(parts))
        raise TemplateDoesNotExist(error)
    load_template_source.is_usable = True
