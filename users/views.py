import json
import math
import random
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from users.serializers import ImageSerializer, MyTokenObtainPairSerializer, SendPasswordResetEmailSerializer, UserBidsLeftSerializer, UserNotificationSerializer, UserSettingSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer, UserUpdateSerializer, UserUsernameSerializer
from django.contrib.auth import authenticate
from users.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework import generics
from cars.models import Bid, Car
from .models import User, UserNotification, UserProfilePicture, UserSetting
from .utils import Util
from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache


def generateOTP() :

  string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
  OTP = ""
  length = len(string)
  for i in range(6) :
    OTP += string[math.floor(random.random() * length)]

  return OTP

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    otp = generateOTP()
    request.data['otp'] = otp
    link = ''
    body = otp + " " + link
    data = {
      'subject':'Registeration otp for Addis Offer',
      'body':body,
      'to_email': request.data['email']
    }
    Util.send_email(data)

    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)

class OTPVerificationView(APIView):
  def post(self, request, format=None):
    try:
      user = User.objects.get(otp = request.data['otp'])
      user.verified = True
      user.save()
      return Response({'msg':'Verfied'}, status=status.HTTP_200_OK)
    except:
      return Response({'msg':'OTP not matched'}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.GenericAPIView):
  renderer_classes = [UserRenderer]
  permission_classes = (permissions.AllowAny,)
  serializer_class = MyTokenObtainPairSerializer

  def post(self, request, format=None):

    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
      if user.verified is not False:
        token = get_tokens_for_user(user)
        return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
      else:
        return Response({'msg':'Account is not verified'}, status=status.HTTP_400_BAD_REQUEST)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]

  def get(self, request, format=None):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

class UserBidsLeftView(APIView):
  renderer_classes = [UserRenderer]

  def get(self, request):
    # geting token from header
    authHeader = request.headers['Authorization']
    access_token_obj = AccessToken(authHeader)
    # user id from access token
    user_id=access_token_obj['user_id']
    # user from user_id
    user = User.objects.get(pk=user_id)
    serializer_class = UserBidsLeftSerializer(user)
    return Response(serializer_class.data)

class UserUsernameView(APIView):
  renderer_classes = [UserRenderer]

  def get(self, request, id=None):
    if id is not None:
      user = User.objects.get(pk=id)
      serializer_class = UserUsernameSerializer(user)
      return Response(serializer_class.data)

class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]

  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]

  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]

  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)

class UserLogoutView(APIView):
  def post(self, _):
    response = Response()
    response.delete_cookie(key="refresh_token")
    response.data = {
      'message': "Logout success!"
    }
    return response

class CommentorImageView(generics.ListCreateAPIView):
  serializer_class = ImageSerializer

  def get(self, request, *args, **kwargs):
    user_id = request.GET.get("user_id")
    image = UserProfilePicture.objects.get(user = user_id)
    
    serializer = self.get_serializer(image)
    return Response(serializer.data['profile_pic'])

class UploadImageView(APIView):
  renderer_classes = [UserRenderer]
  
  def get(self, request, format=None):
    # geting token from header
    authHeader = request.headers['Authorization']
    access_token_obj = AccessToken(authHeader)
    # user id from access token
    user_id=access_token_obj['user_id']
    
    picture = UserProfilePicture.objects.filter(user=user_id)

    serializer = ImageSerializer(picture, many = True)
    return Response(serializer.data, status=status.HTTP_200_OK)

  def post(self, request, format=None):
    serializer = ImageSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=400)
  
  def patch(self, request):
    # geting token from header
    authHeader = request.headers['Authorization']
    access_token_obj = AccessToken(authHeader)
    # user id from access token
    user_id=access_token_obj['user_id']
    
    user_setting = UserProfilePicture.objects.get(user=user_id)
    
    serializer_class = ImageSerializer(user_setting, data=request.data)
    if serializer_class.is_valid():
      serializer_class.save()
      return Response({'msg':'Settings updated!!'}, status=status.HTTP_200_OK)
    return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def retrieve(self, request, pk=None):
    id = pk
    if id is not None:
      user_setting = UserProfilePicture.objects.get(user=id)
      serializer_class = UserSettingSerializer(user_setting)
      return Response(serializer_class.data)

class UserUpdateView(APIView):
  renderer_classes = [UserRenderer]
  serializer_class = UserUpdateSerializer

  def patch(self, request, id=None):
    user = User.objects.get(pk=request.data['id'])
    user.bids_left = request.data['bids_left']
    user.save()
    return Response({'msg':'User Updated Successfully'}, status=status.HTTP_200_OK)

class UsersRegisteredView(APIView):
  renderer_classes = [UserRenderer]
  queryset= User.objects.all()

  def get(self, request):
    users = User.objects.all()
    return Response(len(users), status=status.HTTP_200_OK)

#NOTIFICATIONS AREA
class UserSettingView(viewsets.ModelViewSet):
  renderer_classes = [UserRenderer]
  serializer_class = UserSettingSerializer
  permission_classes = [IsAuthenticated]
  queryset= UserSetting.objects.all()

  def get(self, request, format=None):
    serializer = UserSettingSerializer()
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  def post(self, request, format=None):
    user = request.user
    user.notification_is_replied = request.data['notification_is_replied']
    user.notification_is_sound = request.data['notification_is_sound']
    user.notification_is_new_bid = request.data['notification_is_new_bid']
    user.email_is_auction_end = request.data['email_is_auction_end']
    user.email_is_new_bid = request.data['email_is_new_bid']
    user.email_is_new_comment = request.data['email_is_new_comment']
    user.email_is_out_bid = request.data['email_is_out_bid']
    user.save()
    return Response({'msg':'Settings updated'}, status=status.HTTP_200_OK)
  
  def retrieve(self, request, pk=None):
    id = pk
    if id is not None:
      user_setting = UserSetting.objects.get(user=id)
      serializer_class = UserSettingSerializer(user_setting)
      return Response(serializer_class.data)
  
  def partial_update(self, request, pk=None):
    id = pk
    user_setting = UserSetting.objects.get(user=id)
    serializer_class = UserSettingSerializer(user_setting, data=request.data)

    if serializer_class.is_valid():
        serializer_class.save()
        return Response({'msg':'Settings updated!!'}, status=status.HTTP_200_OK)
    return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailIsAuctionEndView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    car_id = request.data['car_id']
    car = Car.objects.get(id = car_id)
    user_id = car.seller.id
    user = User.objects.get(id = user_id)
    setting = UserSetting.objects.get(user=user)

    if setting.email_is_auction_end:
      body = 'Notify me when my auction ends'
      data = {
        'subject':'Your auction has ended',
        'body':body,
        'to_email':user.email
      }
      Util.send_email(data)
    return Response({'msg':'notified'}, status=status.HTTP_200_OK)

class EmailIsNewBidView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    car_id = request.data['car_id']
    car = Car.objects.get(id = car_id)
    user_id = car.seller.id
    user = User.objects.get(id = user_id)
    setting = UserSetting.objects.get(user=user)

    if setting.email_is_new_bid:
      body = 'Notify me when new bid'
      data = {
        'subject':'New bid on your car',
        'body':body,
        'to_email':user.email
      }
      Util.send_email(data)

    return Response({'msg':'notified'}, status=status.HTTP_200_OK)

class EmailIsNewCommentView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    car_id = request.data['car_id']
    car = Car.objects.get(id = car_id)
    user_id = car.seller.id
    user = User.objects.get(id = user_id)
    setting = UserSetting.objects.get(user=user)

    if setting.email_is_new_comment:
      body = 'Notify me when new Comment'
      data = {
        'subject':'New comment on your car',
        'body':body,
        'to_email':user.email
      }
      Util.send_email(data)

    return Response({'msg':'notified'}, status=status.HTTP_200_OK)

class EmailIsOutBidView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    car_id = request.data['car_id']
    car = Car.objects.get(id = car_id)
    if request.data['last_bid'] != 0:
      bid = Bid.objects.filter(bid_amount=request.data['last_bid'])
      user_id = bid[0].bidder.id
      user = User.objects.get(id = user_id)
      setting = UserSetting.objects.get(user=user)

      if setting.email_is_out_bid:
        body = 'Notify me when new Comment'
        data = {
          'subject':'You have been out bid',
          'body':body,
          'to_email':user.email
        }
        Util.send_email(data)

    return Response({'msg':'notified'}, status=status.HTTP_200_OK)

class UserNotificationView(APIView):
  renderer_classes = [UserRenderer]
  queryset= UserNotification.objects.all()

  def post(self, request):
    user = request.user
    user.notifier = request.data['notifier']
    user.detail = request.data['detail']
    user.notification_type = request.data['notification_type']
    user.notified_time = request.data['notified_time']
    user.save()
    return Response({'msg':'Settings updated'}, status=status.HTTP_200_OK)

  def get(self, request):
    # geting token from header
    authHeader = request.headers['Authorization']
    access_token_obj = AccessToken(authHeader)
    # user id from access token
    user_id=access_token_obj['user_id']
    # user from user_id
    notifications = UserNotification.objects.filter(user=user_id)
    serializer_class = UserNotificationSerializer(notifications, many=True)
    return Response(serializer_class.data)
  
  def delete(self, request, id, format=None):
    notification = UserNotification.objects.filter(id=id)
    notification.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)