from django.test import TestCase

from ex.models import Symbol, Depo, LimitOrder, AbstractOrder, MarketOrder
from services.DTO_service import (
    create_market_order_dto,
    dto_to_order,
    create_random_limit_order_dto,
)


class TestDTO(TestCase):
    def test_market_dto(self):
        Symbol.objects.create(ticker="TLST", full_name="TLSTFN")
        depo = Depo.objects.create(is_algo=False, start_equity=10_000)
        dto = create_market_order_dto(depo.pk, "TLST")
        order = dto_to_order(dto)
        self.assertEqual(order.status, AbstractOrder.OrderStatus.INITIATED)
        self.assertIsInstance(order, MarketOrder)

    def test_limit_dto(self):
        Symbol.objects.create(ticker="TLST", full_name="TLSTFN")
        depo = Depo.objects.create(is_algo=False, start_equity=10_000)
        dto = create_random_limit_order_dto(depo.pk, "TLST")
        order = dto_to_order(dto)
        self.assertEqual(order.status, AbstractOrder.OrderStatus.INITIATED)
        self.assertIsInstance(order, LimitOrder)
