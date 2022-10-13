from rest_framework import routers
from django.urls import path, include
from cars.views import AllowedBidViewSet, CarImagesViewSet, CarMainImageViewSet, CarResultViewSet, CarStatusViewSet, CarTimeViewSet, CarViewSet, BidViewSet, CarsEndedView, PublishedCommentViewSet, UserCarsViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register('', CarViewSet, basename='cars')

# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('/cars/', include(router.urls)),
    path('/cars-images/', CarImagesViewSet.as_view()),
    path('/bids/', BidViewSet.as_view()),
    path('/allowed-bid/', AllowedBidViewSet.as_view()),
    path('/comments/', PublishedCommentViewSet.as_view()),
    path('/cars-status-end/', CarStatusViewSet.as_view()),
    path('/car-time/<int:pk>/', CarTimeViewSet.as_view()),
    path('/user-cars/', UserCarsViewSet.as_view()),
    path('/car-results/', CarResultViewSet.as_view({'get': 'list'})),
    path("/main-image/", CarMainImageViewSet.as_view()),
    path("/auctions-completed/", CarsEndedView.as_view())
]