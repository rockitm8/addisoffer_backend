from dataclasses import field
from django.contrib import admin
from users.models import User, UserNotification, UserProfilePicture, UserSetting
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserModelAdmin(BaseUserAdmin):

    list_display = ('id', 'email', 'user_name', 'bids_left', 'verified',)
    list_filter = ('email',)
    fieldsets = (
        ('Personal info', {'fields': ('email', 'user_name', 'password',)}),
        ('Permissions', {'fields': ('bids_left', 'is_admin', 'verified')}),
    )

    add_fieldsets= (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'password1', 'password2',),
        }),
    )

    search_fields = ('email', 'user_name',)
    ordering = ('email', 'id',)
    filter_horizontal = ()

class UserSettingModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

class UserProfilePicModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'profile_pic')

class UserNotificationModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notifier', 'detail', 'notification_type', 'notified_time')

admin.site.register(User, UserModelAdmin)
admin.site.register(UserSetting, UserSettingModelAdmin)
admin.site.register(UserProfilePicture, UserProfilePicModelAdmin)
admin.site.register(UserNotification, UserNotificationModelAdmin)