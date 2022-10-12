from email.policy import default
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser

#  Custom User Manager
class UserManager(BaseUserManager):
  def create_user(self, email, user_name, password=None, password2=None, bids_left=0, otp=None):
      """
      Creates and saves a User with the given email, name, tc and password.
      """
      if not email:
          raise ValueError('User must have an email address')

      user = self.model(
          email=self.normalize_email(email),
          user_name=user_name,
          bids_left = bids_left,
          otp = otp,
      )
      user.set_password(password)
      user.is_admin = False
      user.save(using=self._db)
      return user

  def create_superuser(self, email, user_name, password=None, bids_allowed=0, otp='000000'):
      """
      Creates and saves a superuser with the given email, name, tc and password.
      """
      user = self.create_user(
          email,
          password=password,
          user_name=user_name,
          otp=otp
      )
      user.verified = True
      user.is_admin = True
      user.save(using=self._db)
      return user

#  Custom User Model
class User(AbstractBaseUser):
  email = models.EmailField(
      verbose_name='Email',
      max_length=255,
      unique=True,
  )
  user_name = models.CharField(max_length=200, unique=True)
  is_active = models.BooleanField(default=True)
  is_admin = models.BooleanField(default=False)
  bids_left = models.IntegerField("Bids Left", default=0)
  otp = models.CharField(max_length=6, default="000000")
  verified = models.BooleanField(default=False)

  objects = UserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['user_name']

  def __str__(self):
    return self.user_name

  def has_perm(self, perm, obj=None):
      "Does the user have a specific permission?"
      # Simplest possible answer: Yes, always
      return self.is_admin

  def has_module_perms(self, app_label):
      "Does the user have permissions to view the app `app_label`?"
      # Simplest possible answer: Yes, always
      return True

  @property
  def is_staff(self):
      "Is the user a member of staff?"
      # Simplest possible answer: All admins are staff
      return self.is_admin

class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    notification_is_replied = models.BooleanField('Notification_is_replied', default=1)
    notification_is_new_bid = models.BooleanField('Notification_is_new_bid', default=1)
    notification_is_sound = models.BooleanField('notifications_is_sound', default=1)
    email_is_auction_end = models.BooleanField('Email_is_auction_end', default=1)
    email_is_new_bid = models.BooleanField('Email_is_new_bid', default=1)
    email_is_new_comment = models.BooleanField('Email_is_new_comment', default=1)
    email_is_out_bid = models.BooleanField('Email_is_out_bid', default=1)

    def __str__(self):
        return str(self.id)

NOTIFICATION_TYPES = (('notification_is_replied','notification_is_replied'), ('notification_is_new_bid', 'notification_is_new_bid'))
class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notifier = models.CharField('Notifier', max_length=50)
    detail = models.CharField('Detail', max_length=100)
    notification_type = models.CharField('Notification Type', max_length=30, choices=NOTIFICATION_TYPES, default='notification_is_replied')
    notified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

class UserProfilePicture(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField('Profile Picture', null=True, blank=True)