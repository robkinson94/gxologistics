from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from core.views import ( CookieTokenObtainPairView, CookieTokenRefreshView, logout_view, get_csrf_token)

urlpatterns = [
    path("mis_admin_page/", admin.site.urls),
    path("api/", include("core.urls")),
    path('api/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', logout_view, name='logout'),
    path('api/csrf/', get_csrf_token, name='get_csrf'),
    path('api/me/', get_csrf_token, name='me'),
]

if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
