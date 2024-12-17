"""
URL configuration for myex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django_registration.views import RegistrationView

import ex.models
from ex.views import symbol_view, symbol_view_api, homepage_view, HomepageAPI

# from users.views import register

# from orders.views import OrderViewSet

# router = SimpleRouter()

# router.register(r'order', OrderViewSet)


urlpatterns = [
    path("api/", HomepageAPI.as_view()),
    path("", homepage_view, name="homepage"),
    path("users/", include("users.urls")),
    path("admin/", admin.site.urls),
    path("", include("ex.urls")),
]

# urlpatterns += router.urls
