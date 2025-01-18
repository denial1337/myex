from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import JsonResponse
from django.http import HttpRequest

from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from itertools import chain

from urllib3 import HTTPResponse

from services.DTO_service import dto_to_order, api_request_to_dto, view_request_to_order
from services.broker_service import get_pnl, free_equity
from services.context_service import get_context_by_ticker
from services.order_book_service import get_serialized_order_book
from services.symbol_service import get_symbol_by_ticker
from services.transaction_service import resolve_order
from .models import Symbol, Depo, Position, LimitOrder, MarketOrder

ORDERS_NUM = 7


def symbol_view(request: HttpRequest, ticker: str) -> HTTPResponse:
    if request.method == "GET":
        context = get_context_by_ticker(ticker)
        return render(request, "symbol.html", context)

    if request.method == "POST":
        status = -1
        order = view_request_to_order(request, ticker)
        resolve_order(order)
        context = get_context_by_ticker(ticker)
        context["is_auth"] = request.user.is_authenticated
        context["status"] = status
        return render(request, "symbol.html", context)


@csrf_exempt
def symbol_view_api(request: HttpRequest, ticker: str) -> JsonResponse:
    if (symbol := get_symbol_by_ticker(ticker)) is None:
        return JsonResponse(f'ticker "{ticker}" does not exist')

    if request.method == "GET":
        ob = get_serialized_order_book(symbol)
        return JsonResponse({"order_book": ob})

    if request.method == "POST":
        dto = api_request_to_dto(request)
        order = dto_to_order(dto)
        if order is not None:
            resolve_order(order)
        return JsonResponse({})


@csrf_exempt
def user_depo_api(request: HttpRequest, user_pk: int) -> JsonResponse:
    if request.method == "GET":
        try:
            user = User.objects.get(pk=user_pk)
        except ObjectDoesNotExist:
            return JsonResponse({"error": f"No depo with user pk {user_pk}"})
        depo = Depo.objects.get(user=user)
        return JsonResponse(
            {"current_equity": depo.current_equity, "free_equity": free_equity(depo)}
        )


@csrf_exempt
def user_positions_api(request: HttpRequest, user_pk: int) -> JsonResponse:
    if request.method == "GET":
        try:
            user = User.objects.get(pk=user_pk)
        except ObjectDoesNotExist:
            return JsonResponse({"error": f"No depo with user pk {user_pk}"})
        depo = Depo.objects.get(user=user)
        if depo is None:
            return JsonResponse({"error": f"No depo with user pk {user_pk}"})
        positions = Position.objects.filter(Q(depo=depo) & ~Q(quantity=0))
        pnls = [get_pnl(pos) for pos in positions]
        print(pnls, positions)
        positions = [model_to_dict(pos) for pos in positions if pos.quantity != 0]
        for pos, pnl in zip(positions, pnls):
            pos["symbol"] = Symbol.objects.get(pk=pos["symbol"]).ticker
            pos["pnl"] = pnl
        return JsonResponse({"positions": positions})


@csrf_exempt
def user_orders_api(request: HttpRequest, user_pk: int) -> HttpRequest:
    if request.method == "GET":
        try:
            user = User.objects.get(pk=user_pk)
        except ObjectDoesNotExist:
            return JsonResponse({"error": f"No user with user pk {user_pk}"})
        depo = Depo.objects.get(user=user)
        limit_orders = (
            LimitOrder.objects.filter(initiator=depo)
            .order_by("-pk")[:ORDERS_NUM]
            .values(
                "id",
                "direction",
                "datetime",
                "status",
                "initial_quantity",
                "quantity",
                "symbol",
                "price",
            )
        )
        for order in limit_orders:
            order["order_type"] = "LIMIT"
        market_orders = (
            MarketOrder.objects.filter(initiator=depo)
            .order_by("-pk")[:ORDERS_NUM]
            .values(
                "id",
                "direction",
                "datetime",
                "status",
                "initial_quantity",
                "quantity",
                "symbol",
            )
        )
        for order in market_orders:
            order["order_type"] = "MARKET"
        orders = list(chain(limit_orders, market_orders))
        orders = sorted(orders, key=lambda x: x["datetime"], reverse=True)[:ORDERS_NUM]

        for order in orders:
            order["symbol"] = Symbol.objects.get(pk=order["symbol"]).ticker
        return JsonResponse({"orders": orders})


@csrf_exempt
def depo_view_api(request: HttpRequest, depo_pk: int) -> JsonResponse:
    if request.method == "GET":
        depo = Depo.objects.get(pk=depo_pk)
        if depo is None:
            return JsonResponse({"error": f"No depo with pk {depo_pk}"})


class HomepageAPI(View):
    def get(self, request, *args, **kwargs):
        symbols = Symbol.objects.all()

        tickers = list(Symbol.objects.all().values("ticker"))
        return JsonResponse({"symbols": tickers})


def homepage_view(request: HttpRequest) -> HTTPResponse:
    if request.method == "GET":
        return render(request, "homepage.html")
