from django.db.models import Sum
from django.http import Http404
from django.test import TestCase

from ex.models import Symbol, Depo, LimitOrder, AbstractOrder, MarketOrder
from generate import generate_symbols, generate_deposits
from services.DTO_service import OrderDTO, MarketOrderDTO, OrderType, OrderDirection, create_dto_market_order, \
    dto_to_order, create_dto_limit_order


class TestDTO(TestCase):
    def test_market_dto(self):
        Symbol.objects.create(ticker='TLST', full_name='TLSTFN')
        depo = Depo.objects.create(is_algo=False, start_equity=10_000)
        dto = create_dto_market_order(depo.pk, 'TLST')
        order = dto_to_order(dto)
        self.assertEqual(order.status, AbstractOrder.OrderStatus.INITIATED)
        self.assertIsInstance(order, MarketOrder)

    def test_limit_dto(self):
        Symbol.objects.create(ticker='TLST', full_name='TLSTFN')
        depo = Depo.objects.create(is_algo=False, start_equity=10_000)
        dto = create_dto_limit_order(depo.pk, 'TLST')
        order = dto_to_order(dto)
        self.assertEqual(order.status, AbstractOrder.OrderStatus.INITIATED)
        self.assertIsInstance(order, LimitOrder)