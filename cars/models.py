from unicodedata import name
from django.db import models
from users.models import User
from django import forms

# Create your models here.

CAR_STATUS = (('pending','PENDING'), ('listed', 'LISTED'), ('ended','ENDED'))

class Car(models.Model):
  vin_number = models.CharField('VIN Number', max_length=20, unique=True)
  seller = models.ForeignKey(User, on_delete=models.CASCADE)
  seller_name = models.CharField('Seller Name', max_length=50)
  reserve_bid = models.IntegerField('Reserve Bid', blank=True, default=0)
  high_bid = models.IntegerField('Highest Bid', default=0)
  total_bids = models.IntegerField('Total Bids', default=0)
  total_comments = models.IntegerField('Total Comments', default=0)
  time_left = models.DateTimeField('Time Left')
  bid_days = models.IntegerField('Bidding Days')
  seller_type = models.CharField('Seller Type', max_length=10)
  year = models.IntegerField('Year')
  make = models.CharField('Make', max_length=30)
  model = models.CharField('Model', max_length=30)
  body_type = models.CharField('Body Type', max_length=20)
  engine = models.CharField('Engine', max_length=20)
  interior_color = models.CharField('Interior Color', max_length=30)
  exterior_color = models.CharField('Exterior Color', max_length=30)
  transmission = models.CharField('Transmission', max_length=10)
  condition = models.CharField('Condition', max_length=30)
  mileage = models.IntegerField('Mileage')
  gas_type = models.CharField('Gas Type', max_length=20)
  plate_code = models.CharField('Plate Code', max_length=30)
  location = models.CharField('Location', max_length=50)
  phone_number = models.CharField('Phone Number', max_length=20)
  coupon_code = models.CharField('Coupon Code', max_length=20, blank=True)
  highlight_modification = models.TextField('Highlight/Modification', max_length=200)
  known_flaws = models.TextField('Known Flaws', max_length=200)
  other_info = models.TextField('Other Information', max_length=200)
  car_status = models.CharField('Car Status', max_length=7, choices=CAR_STATUS, default='pending')
  views = models.IntegerField('Views', default=0)


  def __str__(self):
    carName = str(self.year) + " " + self.make + " " + self.model
    return carName

class CarImage(models.Model):
  car = models.ForeignKey(Car, on_delete=models.CASCADE)
  image = models.ImageField('Car Image', null=True, blank=True)

  def __str__(self):
    return str(self.car)


class Bid(models.Model):
  bidder = models.ForeignKey(User, on_delete=models.CASCADE) 
  bid_on = models.ForeignKey(Car, on_delete=models.CASCADE) 
  bid_amount = models.IntegerField('Amount')

  def __str__(self):
    return str(self.id)

class PublishedComment(models.Model):
  commentor = models.ForeignKey(User, on_delete=models.CASCADE)
  commentor_name = models.CharField('Commentor Name', max_length=50, default='None')
  commented_on = models.ForeignKey(Car, on_delete=models.CASCADE) 
  comment = models.TextField('Comment', max_length=100)
  commentor_type = models.CharField('Commentor Type', max_length=100, default='None')
  reply_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_requests_created', null=True, blank=True)
  published_time = models.DateTimeField(auto_now=True)

  def __str__(self):
    return str(self.id)