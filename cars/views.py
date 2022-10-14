import datetime
from datetime import datetime, timedelta
from functools import partial
import json
from logging import exception
from urllib.parse import ParseResultBytes
from rest_framework import viewsets, generics
from rest_framework.response import Response
from cars.models import AllowedBid, Car, Bid, CarImage, PublishedComment
from cars.serializers import AllowedBidSerializer, CarImageSerializer, CarSerializer, BidSerializer, PublishedCommentSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from users.models import User
from rest_framework.views import APIView
from django.core.files.base import ContentFile

# Create your views here.

# ViewSets define the view behavior.
class CarViewSet(viewsets.ViewSet):
    queryset= Car.objects.all()
    serializer_class = CarSerializer

    def list(self, request):
        cars = Car.objects.filter(car_status = "listed")
        serializer_class = CarSerializer(cars, many=True)
        return Response(serializer_class.data)
    
    def retrieve(self, request, pk=None):
        id = pk
        if id is not None:
            car = Car.objects.get(pk=id)
            serializer_class = CarSerializer(car)
            return Response(serializer_class.data)

    def create(self, request):
        serializer_class = CarSerializer(data=request.data)
        request.data._mutable = True
        authHeader = request.headers['Authorization']
        access_token_obj = AccessToken(authHeader)
        user_id=access_token_obj['user_id']
        request.data['seller'] = user_id
        
        
        currentDateTime = datetime.utcnow()
        closingDateTime = currentDateTime + timedelta(days=int(request.data['bid_days']))
        request.data['time_left'] = closingDateTime

        if serializer_class.is_valid():
            serializer_class.save()
            images = [i for (x, i) in request.data.items() if ("image") in x]

            for item in images:
                CarImage.objects.create(car=Car.objects.get(id=serializer_class.data['id']), image=item)
            return Response({'msg':'Car data submitted'}, status=status.HTTP_201_CREATED)
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk):
        id = pk
        car = Car.objects.get(pk=id)
        car.delete()
        return Response({'msg','Car Data Deleted'})

    def partial_update(self, request, pk=None):
        id = pk
        car = Car.objects.get(pk=id)
        serializer_class = CarSerializer(car, data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            return Response({'msg':'Car data updated!!'}, status=status.HTTP_200_OK)
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCarsViewSet(APIView):
    queryset= Car.objects.all()
    serializer_class = CarSerializer
    
    def get(self, request):
        # getting token from header
        authHeader = request.headers['Authorization']
        access_token_obj = AccessToken(authHeader)
        # user id from access token
        user_id=access_token_obj['user_id']
        cars = Car.objects.filter(seller = user_id)
        
        serializer_class = CarSerializer(cars, many=True)
        return Response(serializer_class.data)

class CarImagesViewSet(generics.ListCreateAPIView):
    serializer_class = CarImageSerializer
    queryset = CarImage.objects.all()
    
    def get(self, request, *args, **kwargs):
        car_id = request.GET.get("car_id")
        images = CarImage.objects.filter(car = car_id)
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)

class CarMainImageViewSet(generics.ListCreateAPIView):
    serializer_class = CarImageSerializer
    queryset = CarImage.objects.all()

    def get(self, request, *args, **kwargs):
        car_id = request.GET.get("car_id")
        images = CarImage.objects.filter(car = car_id)
        
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data[0]['image'])

class CarResultViewSet(viewsets.ViewSet):
    queryset= Car.objects.all()
    serializer_class = CarSerializer
    
    def list(self, request):
        cars = Car.objects.filter(car_status = "ended")
        serializer_class = CarSerializer(cars, many=True)
        return Response(serializer_class.data)

class CarsEndedView(APIView):
  queryset= Car.objects.all()
  serializer_class = CarSerializer

  def get(self, request):
    cars = Car.objects.filter(car_status = "ended")
    serializer_class = CarSerializer(cars, many=True)
    cars_value = 0
    for car in serializer_class.data:
        cars_value += car['high_bid']
    
    data = {
        'auctions_completed': len(serializer_class.data),
        'value_cars_sold': cars_value
    }
    return Response(data, status=status.HTTP_200_OK)

class CarStatusViewSet(generics.ListCreateAPIView):
    serializer_class = CarSerializer
    def post(self, request):
        try:
            car_id = request.data['car_id']
            car = Car.objects.get(id = car_id)
            car.car_status = 'ended'
            car.save()
            return Response({'msg':'Auction ended'}, status=status.HTTP_200_OK)
        except:
            return Response({'msg':'car_id not found'}, status=status.HTTP_400_BAD_REQUEST)

class CarTimeViewSet(generics.UpdateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def perform_update(self, serializer):
        new_time = datetime.utcnow() + timedelta(minutes=5)
        serializer.save(time_left=new_time)

class BidViewSet(generics.ListCreateAPIView):
    serializer_class = BidSerializer
    queryset= Bid.objects.all()
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # geting token from header
        authHeader = request.headers['Authorization']
        access_token_obj = AccessToken(authHeader)
        # user id from access token
        user_id=access_token_obj['user_id']
        # user from user_id
        user = User.objects.get(pk = user_id)
        # accessing car id
        bid_on = request.data['bid_on']

        car = Car.objects.filter(id = bid_on)
        if car[0].seller.id == user_id:
            return

        request.data['bid_on'] = bid_on
        request.data['bidder'] = user_id

        return self.create(request, *args, **kwargs)


class AllowedBidViewSet(generics.ListCreateAPIView):
    serializer_class = AllowedBidSerializer
    queryset= AllowedBid.objects.all()
    
    def get(self, request, *args, **kwargs):
        # geting token from header
        authHeader = request.headers['Authorization']
        access_token_obj = AccessToken(authHeader)
        # user id from access token
        user_id=access_token_obj['user_id']
        # user from user_id
        user = AllowedBid.objects.filter(user = user_id)
        car_id = request.GET.get("car_id")
        car = AllowedBid.objects.filter(car = car_id)
        
        if not user:
            return Response(False, status=status.HTTP_200_OK)
        if not car:
            return Response(False, status=status.HTTP_200_OK)

        return Response(True, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # geting token from header
        authHeader = request.headers['Authorization']
        access_token_obj = AccessToken(authHeader)
        # user id from access token
        user_id=access_token_obj['user_id']
        # user from user_id
        user = User.objects.filter(id = user_id)
        # accessing car id
        car_id = request.data['bid_on']
        car = Car.objects.filter(id = car_id)

        request.data['user'] = user[0]
        request.data['car'] = car[0]

        return self.create(request, *args, **kwargs)



class PublishedCommentViewSet(generics.ListCreateAPIView):
    serializer_class = PublishedCommentSerializer
    queryset = PublishedComment.objects.all()

    def get(self, request, *args, **kwargs):
        car_id = request.GET.get("car_id")
        comments = PublishedComment.objects.filter(commented_on = car_id)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # geting token from header
        authHeader = request.headers['Authorization']
        access_token_obj = AccessToken(authHeader)
        # user id from access token
        user_id=access_token_obj['user_id']
        # user from user_id
        user = User.objects.get(pk = user_id)
        # accessing car id
        commented_on = request.data['commented_on']
        # car object from car_id
        car = Car.objects.filter(id = commented_on)

        if car[0].seller.id == user_id:
            request.data['commentor_type'] = 'seller'
        else:
            bidders = Bid.objects.filter(bid_on = car[0]).filter(bidder = user_id)
            if bidders:
                request.data['commentor_type'] = 'bidder'
        request.data['commented_on'] = commented_on
        request.data['commentor'] = user_id
        request.data['commentor_name'] = user.user_name

        return self.create(request, *args, **kwargs)