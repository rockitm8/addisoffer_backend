from django.core.mail import EmailMessage
import os
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from users.models import UserNotification, UserSetting, User, UserProfilePicture
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from users.utils import Util
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status


class UserRegistrationSerializer(serializers.ModelSerializer):
  password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
  
  class Meta:
    model = User
    fields = ['email', 'user_name', 'password', 'password2', 'otp']
    extra_kwargs = {
      'password':{'write_only':True}
    }

  def validate(self, data):
    password = data.get('password')
    password2 = data.get('password2')
    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    return data

  def create(self, validated_data):
    user = User.objects.create_user(**validated_data)
    Token.objects.create(user=user)
    UserSetting.objects.create(user=user)
    UserProfilePicture.objects.create(user=user)
    return user

class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'email', 'user_name']

class UserBidsLeftSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['bids_left']

class UserUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['bids_left']

class UserUsernameSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['user_name']

class UserChangePasswordSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, data):
    password = data.get('password')
    password2 = data.get('password2')
    user = self.context.get('user')
    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    user.set_password(password)
    user.save()
    return data

class SendPasswordResetEmailSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    fields = ['email']

  def validate(self, data):
    email = data.get('email')
    if User.objects.filter(email=email).exists():
      user = User.objects.get(email = email)
      uid = urlsafe_base64_encode(force_bytes(user.id))
      token = PasswordResetTokenGenerator().make_token(user)
      link = 'http://addisoffer.com/en/reset-password/'+uid+'/'+token
      # Send Email
      body = '<img style="width:100px;" class="img1" src="http://admin.addisoffer.com/images/Picture1.png" alt="" /><img style="width:200px;" class="img2" src="http://admin.addisoffer.com/images/Picture2.png" alt="" /><p>Need to reset your password?</p><p>Here is your secret link!</p><p>' + link + '</p><p>If you did not forget your password, you can ignore this email.</p><p>If you didn’t make this request, then you can ignore this email 🙂</p><p>Kind Regards,</p><p>The Addis Offer Team</p>'
      msg = EmailMessage(subject='Reset Your Password', body=body, from_email=os.environ.get('EMAIL_FROM'), to=[user.email])
      msg.content_subtype = "html"  # Main content is now text/html
      msg.send()
      
      return msg
    else:
      raise serializers.ValidationError('You are not a Registered User')

class UserPasswordResetSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, data):
    try:
      password = data.get('password')
      password2 = data.get('password2')
      uid = self.context.get('uid')
      token = self.context.get('token')
      if password != password2:
        raise serializers.ValidationError("Password and Confirm Password doesn't match")
      id = smart_str(urlsafe_base64_decode(uid))
      user = User.objects.get(id=id)
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise serializers.ValidationError('Token is not Valid or Expired')
      user.set_password(password)
      user.save()
      return data
    except DjangoUnicodeDecodeError as identifier:
      PasswordResetTokenGenerator().check_token(user, token)
      raise serializers.ValidationError('Token is not Valid or Expired')
  
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):
    data = {}
    try:
      data = super(MyTokenObtainPairSerializer, self).validate(attrs)
    except:
      data.update({'msg': "Username or password is incorrect!!"})
    
    return data

  @classmethod
  def get_token(cls, user):
    token = super(MyTokenObtainPairSerializer, cls).get_token(user)
    return token

class ImageSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserProfilePicture
    fields = ['id', 'profile_pic']

class UserSettingSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserSetting
    fields = ['notification_is_replied', 'notification_is_sound',
    'notification_is_new_bid', 'email_is_auction_end', 'email_is_new_bid', 'email_is_new_comment',
    'email_is_out_bid']

class UserNotificationSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserNotification
    fields = ['id', 'notifier', 'detail', 'notification_type', 'notified_time']