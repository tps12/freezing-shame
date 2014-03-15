from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

uuid = '[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'freezing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'shame.views.index'),
    url(r'^(' + uuid + ')$', 'shame.views.detail'),
    url(r'^cart$', 'shame.views.cart'),
    url(r'^admin/', include(admin.site.urls)),
)
