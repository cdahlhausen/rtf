from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/', auth_views.login, {'template_name': 'rtfapp/login.html'}, name='login'),
    #To appease builtin views (for now)
    url(r'^accounts/login', auth_views.login, {'template_name': 'rtfapp/login.html'}, name='alt_login'),
    url(r'^logout/', auth_views.logout, {'template_name': 'rtfapp/index.html'}, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^password_change/$', auth_views.password_change, {'post_change_redirect': '/administration/'}, name='password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset,  name='password_reset'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password_reset_done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^password_reset_complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^edit-profile/$', views.edit_profile, name='edit_profile'),
    url(r'^administration/$', views.administration, name='administration'),
    url(r'^downloadKMZ/$', views.downloadKMZ, name='downloadKMZ'),
    url(r'^downloadDB/$', views.downloadDB, name='downloadDB'),
    url(r'^uploadDB/$', views.uploadDB, name='uploadDB'),
    url(r'^maintenance-requests/$', views.maintenance_requests, name='maintenance_requests'),
    url(r'^placemarks/$', views.placemarks, name='placemarks '),
    url(r'^maintenance-requests/(?P<pk>\d+)/$', views.maintenance_requests, name='maintenance_requests'),
    url(r'^submit_request/$', views.submit_request, name='submit_request'),
    url(r'^queue-intersection/$', views.queue_intersection, name='queue_intersection'),
    url(r'^parcels/$', views.parcels, name='parcels'),
    url(r'^parcels/statuses/$', views.parcel_statuses, name='parcel_statuses'),
    url(r'^parcels/statuses/(?P<pk>\d+)/$', views.parcel_statuses, name='parcel_statuses_pk')
]
