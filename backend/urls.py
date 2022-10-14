from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

...

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

# from vueapp import views as vueapp_views

urlpatterns = [
   path('api', include('cars.urls')),
   path('api/users/', include('users.urls')),
   path('admin/', admin.site.urls),
   # path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))