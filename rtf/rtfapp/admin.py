from django.contrib import admin
from .models import TrailSegment, MaintenanceRequest, Atom
from .models import Parcel, UserProfile, Permission, IntersectionTask


admin.site.register(Permission)
admin.site.register(Atom)
admin.site.register(TrailSegment)
admin.site.register(MaintenanceRequest)
admin.site.register(Parcel)
admin.site.register(UserProfile)
admin.site.register(IntersectionTask)