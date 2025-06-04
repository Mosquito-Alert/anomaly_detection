from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns(
    '',
    # host(r'api', settings.ROOT_URLCONF, name='api'),
)
