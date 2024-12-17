from django.test import TestCase

from ex.models import Symbol, Depo, LimitOrder, AbstractOrder, MarketOrder
from services.order_validation_service import is_valid_order
from services.transaction_service import resolve_order


class TestSymbol(TestCase):
    def test_market_order_validation(self):
        ticker = "mov"
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + "fn")
        maker_depo = Depo.objects.create(start_equity=10000)
        taker_depo = Depo.objects.create(start_equity=10000)
        lo1 = LimitOrder.objects.create(
            initiator=maker_depo,
            symbol=symbol,
            direction=AbstractOrder.OrderDirection.BUY,
            price=500,
            quantity=5,
        )
        lo2 = LimitOrder.objects.create(
            initiator=maker_depo,
            symbol=symbol,
            direction=AbstractOrder.OrderDirection.SELL,
            price=501,
            quantity=3,
        )

        resolve_order(lo1)
        resolve_order(lo2)

        # sell tests

        mo = MarketOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=6,
            direction=AbstractOrder.OrderDirection.SELL,
        )
        self.assertEqual(is_valid_order(mo), False)

        mo = MarketOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=1,
            direction=AbstractOrder.OrderDirection.SELL,
        )
        self.assertEqual(is_valid_order(mo), True)

        taker_depo = Depo.objects.create(start_equity=1)
        mo = MarketOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=1,
            direction=AbstractOrder.OrderDirection.SELL,
        )
        self.assertEqual(is_valid_order(mo), False)

        # buy tests
        taker_depo = Depo.objects.create(start_equity=10000)
        mo = MarketOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=4,
            direction=AbstractOrder.OrderDirection.BUY,
        )
        self.assertEqual(is_valid_order(mo), False)

        mo = MarketOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=1,
            direction=AbstractOrder.OrderDirection.BUY,
        )
        self.assertEqual(is_valid_order(mo), True)

        taker_depo = Depo.objects.create(start_equity=1)
        mo = MarketOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=1,
            direction=AbstractOrder.OrderDirection.BUY,
        )
        self.assertEqual(is_valid_order(mo), False)

    def test_limit_order_validation(self):
        ticker = "lov"
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + "fn")
        maker_depo = Depo.objects.create(start_equity=10000)
        taker_depo = Depo.objects.create(start_equity=10000)
        lo1 = LimitOrder.objects.create(
            initiator=maker_depo,
            symbol=symbol,
            direction=AbstractOrder.OrderDirection.BUY,
            price=500,
            quantity=5,
        )
        lo2 = LimitOrder.objects.create(
            initiator=maker_depo,
            symbol=symbol,
            direction=AbstractOrder.OrderDirection.SELL,
            price=501,
            quantity=3,
        )

        resolve_order(lo1)
        resolve_order(lo2)

        # sell tests

        lo = LimitOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=1,
            direction=AbstractOrder.OrderDirection.SELL,
            price=500,
        )
        self.assertEqual(is_valid_order(lo), True)

        lo = LimitOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=6,
            direction=AbstractOrder.OrderDirection.SELL,
            price=500,
        )
        self.assertEqual(is_valid_order(lo), True)

        taker_depo = Depo.objects.create(start_equity=1)
        lo = LimitOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=1,
            direction=AbstractOrder.OrderDirection.SELL,
            price=500,
        )
        self.assertEqual(is_valid_order(lo), False)

        # buy tests
        taker_depo = Depo.objects.create(start_equity=10000)
        lo = LimitOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=4,
            direction=AbstractOrder.OrderDirection.BUY,
            price=501,
        )
        self.assertEqual(is_valid_order(lo), True)

        lo = LimitOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=1,
            direction=AbstractOrder.OrderDirection.BUY,
            price=501,
        )
        self.assertEqual(is_valid_order(lo), True)

        taker_depo = Depo.objects.create(start_equity=1)
        lo = LimitOrder.objects.create(
            initiator=taker_depo,
            symbol=symbol,
            quantity=1,
            direction=AbstractOrder.OrderDirection.BUY,
            price=501,
        )
        self.assertEqual(is_valid_order(lo), False)
