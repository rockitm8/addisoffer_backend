from django.urls import path
from users.views import CommentorImageView, EmailIsAuctionEndView, UserNotificationView, UsersRegisteredView, EmailIsNewBidView, EmailIsNewCommentView, EmailIsOutBidView, OTPVerificationView, SendPasswordResetEmailView, UploadImageView, UserBidsLeftView, UserChangePasswordView, UserLoginView, UserLogoutView, UserProfileView, UserRegistrationView, UserPasswordResetView, UserSettingView, UserUpdateView, UserUsernameView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()
router.register('', UserSettingView, basename='user_setting')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('user/<id>/', UserUsernameView.as_view(), name='username'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('changepassword/', UserChangePasswordView.as_view(), name='change-password'),
    path('reset/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('otp-verification/', OTPVerificationView.as_view(), name='otp-verification'),
    path('image/', UploadImageView.as_view(), name='image'),
    path('profile_pic/<id>/', CommentorImageView.as_view(), name='imagee'),
    path('bids_left/', UserBidsLeftView.as_view(), name='bids'),
    path('update/<id>/', UserUpdateView.as_view(), name='update'),
    path('settings/', include(router.urls)),
    path('registered-members/', UsersRegisteredView.as_view(), name='registered_members'),

    path('email-is-auction-end/', EmailIsAuctionEndView.as_view(), name='email-is-auction-end'),
    path('email-is-new-bid/', EmailIsNewBidView.as_view(), name='email-is-new-bid'),
    path('email-is-new-comment/', EmailIsNewCommentView.as_view(), name='email-is-new-comment'),
    path('email-is-out-bid/', EmailIsOutBidView.as_view(), name='email-is-out-bid'),
    path('notifications/', UserNotificationView.as_view(), name='notification'),
    path('notifications/<id>/', UserNotificationView.as_view(), name='notification_id')
]