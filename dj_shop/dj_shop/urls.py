"""
URL configuration for dj_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('app_users.urls')),
    path('main/', include('app_main.urls')),
    path('', lambda req: redirect('main/')),
    path('i18n', include('django.conf.urls.i18n')),
    path('goods/', include('app_goods.urls')),
    path('basket/', include('app_basket.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]


if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )

    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )