from django.contrib import admin

from main import models


class HospitalInline(admin.StackedInline):
    model = models.main.Hospital


class UserAdmin(admin.ModelAdmin):
    inlines = (HospitalInline,)


class AidAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "status")
    list_filter = ("hospital",)


admin.site.register(models.main.AidRequest, AidAdmin)
admin.site.register(models.user.User, UserAdmin)
