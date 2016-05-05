from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rtf.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rtfapp/', include('rtfapp.urls', namespace="rtfapp")),
    url(r'^', include('rtfapp.urls'))
)
