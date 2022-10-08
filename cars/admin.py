from django.contrib import admin
from cars.models import Car, Bid, CarImage, PublishedComment

# Register your models here.

class SettingCar(admin.ModelAdmin):
    list_display = ('id', 'seller', 'vin_number', 'seller_name', 'car_status', 'views')
    add_fieldsets= (
        (None, {
            'classes': ('wide',),
            'fields': ('vin_number', 'seller_name', 'reserve_bid', 'high_bid', 'total_bids', 
        'total_comments', 'time_left', 'bid_days', 'seller_type', 'year', 'make', 'model',
        'body_type', 'engine', 'interior_color', 'exterior_color', 'interior_color', 'transmission', 
        'condition', 'mileage', 'gas_type', 'plate_code', 'location', 'phone_number', 'coupon_code', 'highlight_modification',
        'known_flaws', 'other_info', 'car_status', 'views'),
        }),
    )

class SettingCarImage(admin.ModelAdmin):
    list_display = ('id', 'car', 'image')

class SettingBid(admin.ModelAdmin):
    list_display = ('id', 'bidder', 'bid_on', 'bid_amount')
    add_fieldsets= (
        (None, {
            'classes': ('wide',),
            'fields': ('bid_amount'),
        }),
    )

class SettingComment(admin.ModelAdmin):
    list_display = ('id', 'commentor', "commentor_name", 'commented_on', "comment", 'commentor_type', 'reply_to', 'published_time')
    add_fieldsets= (
        (None, {
            'classes': ('wide',),
            'fields': ('comment', 'commentor_type'),
        }),
    )

admin.site.register(Car, SettingCar)
admin.site.register(CarImage, SettingCarImage)
admin.site.register(Bid, SettingBid)
admin.site.register(PublishedComment, SettingComment)