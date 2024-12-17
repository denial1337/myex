from django.urls import path, re_path
from ex.views import (
    symbol_view_api,
    symbol_view,
    user_positions_api,
    user_orders_api,
    user_depo_api,
)
import ex.models


urlpatterns = [
    path("api/<str:ticker>/", symbol_view_api),
    path("api/user/<int:user_pk>/depo/", user_depo_api),
    path("api/user/<int:user_pk>/positions/", user_positions_api),
    path("api/user/<int:user_pk>/orders/", user_orders_api),
    re_path(
        r"^(?P<ticker>[A-Z]{1," + str(ex.models.MAX_TICKER_LENGTH) + r"})/$",
        symbol_view,
        name="ticker_view",
    ),
]
