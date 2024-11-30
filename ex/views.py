from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json

from services.DTO_service import OrderType, dto_to_order, requset_to_order, request_to_dto
from services.context_service import get_context_by_ticker, get_chart_url
from services.order_book_service import get_symbol_by_ticker, get_serialized_order_book
from services.transaction_service import create_and_push_limit_order, \
    create_and_push_market_order, resolve_order
from .forms.forms import MarketOrderForm, LimitOrderForm, MarketOrderFormManager, LimitOrderFormManager
from .models import AbstractOrder, Symbol


def order_book(request, ticker):
    symbol = get_symbol_by_ticker(ticker)
    print(request.COOKIES)
    if request.method == 'GET':
        context = get_context_by_ticker(ticker)
        return render(request, 'order_book.html', context)

    if request.method == 'POST':
        print(request.POST)
        btn = request.POST['submit_button']
        btn_short = btn[:3]
        direction = AbstractOrder.OrderDirection.BUY if btn_short == 'buy' \
            else AbstractOrder.OrderDirection.SELL if btn_short == 'sel' else None
        status = -1
        market_form = MarketOrderForm(request.POST)

        if market_form.is_valid() and btn in ['buy_market_btn', 'sell_market_btn']:
            quantity = market_form.cleaned_data['quantity']
            MarketOrderFormManager.form = market_form
            status = create_and_push_market_order(direction=direction, quantity=quantity, symbol=symbol) #FIXME symbol from app
        else:
            limit_form = LimitOrderForm(request.POST)
            if limit_form.is_valid() and btn in ['buy_limit_btn', 'sell_limit_btn']:
                price = limit_form.cleaned_data['price']
                quantity = limit_form.cleaned_data['quantity']
                LimitOrderFormManager.form = limit_form
                status = create_and_push_limit_order(direction=direction, quantity=quantity, symbol=symbol, price=price) #FIXME symbol from app

        context = get_context_by_ticker(ticker)
        context['status'] = status
        return render(request, 'order_book.html', context)

@csrf_exempt
def symbol_view_api(request, ticker):
    print('kek')
    if (symbol := get_symbol_by_ticker(ticker)) is None:
        return HttpResponseNotFound(f'ticker "{ticker}" does not exist')

    if request.method == 'GET':
        ob = get_serialized_order_book(symbol)
        return JsonResponse({'order_book':ob})

    if request.method == 'POST':
        dto = request_to_dto(request)
        order = dto_to_order(dto)
        if not order is None:
            resolve_order(order)
        return JsonResponse({})


class HomepageAPI(View):
    def get(self, request, *args, **kwargs):
        tickers = list(Symbol.objects.all().values('ticker', 'best_bid', 'best_ask'))
        return JsonResponse({'symbols' : tickers})

def homepage_view(request):
    if request.method == 'GET':
        return render(request, 'homepage.html')


