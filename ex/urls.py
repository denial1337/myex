from django.urls import path, re_path
from ex.views import symbol_view_api, order_book
import ex.models


urlpatterns = [
    path('api/<str:ticker>/', symbol_view_api),
    re_path(r'^(?P<ticker>[A-Z]{1,' + str(ex.models.MAX_TICKER_LENGTH) + r'})/$', order_book, name='ticker_view'),
]
