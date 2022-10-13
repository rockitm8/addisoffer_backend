from cars.models import AllowedBid, Car, Bid, CarImage, PublishedComment
from rest_framework import serializers

from users.models import User, UserNotification, UserSetting

# Serializers define the API representation.
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'seller', 'vin_number', 'seller_name', 'reserve_bid', 'high_bid', 'total_bids', 
        'total_comments', 'time_left', 'bid_days', 'seller_type', 'year', 'make', 'model',
        'body_type', 'engine', 'interior_color', 'exterior_color', 'interior_color', 'transmission', 
        'condition', 'mileage', 'gas_type', 'plate_code', 'location', 'phone_number', 'coupon_code', 'highlight_modification',
        'known_flaws', 'other_info', 'views']

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'car', 'image']

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['bidder', 'bid_on', 'bid_amount']
    
    def create(self, validated_data):
        bid = Bid.objects.create(**validated_data)
        car = Car.objects.filter(pk = validated_data['bid_on'].id)
        user = car[0].seller
        setting = UserSetting.objects.filter(user=user)
        if setting[0].notification_is_new_bid:
            carName = str(car[0].year) + " " + car[0].make + " " + car[0].model
            UserNotification.objects.create(user=user, notifier=validated_data['bidder'], detail='has placed a bid on ' + carName, notification_type='notification_is_new_bid')
        return bid

class AllowedBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedBid
        fields = ['id', 'user', 'car']

class PublishedCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishedComment
        fields = ['id', 'commentor', 'commentor_name', 'commented_on', 'comment', 'commentor_type', 'reply_to', 'published_time']

    def create(self, validated_data):
        comment = PublishedComment.objects.create(**validated_data)
        try:
            if validated_data['reply_to'] is not None:
                car = Car.objects.filter(pk = validated_data['commented_on'].id)
                user = User.objects.filter(pk = validated_data['reply_to'].id)
                setting = UserSetting.objects.filter(user=user[0])
                if setting[0].notification_is_replied:
                    carName = str(car[0].year) + " " + car[0].make + " " + car[0].model
                    UserNotification.objects.create(user=user[0], notifier=validated_data['commentor'], detail='has replied to you on ' + carName, notification_type='notification_is_replied')
        except:
            pass
        return comment