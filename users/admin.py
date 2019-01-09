from django.contrib import admin
from . import models
from django.contrib import admin
from django.contrib.auth.models import User


# Register your models here.
class ProfileInline(admin.StackedInline):  # 将UserProfile加入到Admin的user表中
    model = models.Profile
    verbose_name = 'profile'


class ProfileAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)  # 去掉在admin中的注册
# admin.site.register(User, ProfileAdmin)  # 用userProfileAdmin注册user
admin.site.register(User, ProfileAdmin)  # 用userProfileAdmin注册user

"""
admin.site.register(models.Menu)
admin.site.register(models.Area)
admin.site.register(models.UserRequest)
admin.site.register(models.UserResetpsd)
"""
