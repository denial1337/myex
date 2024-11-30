from django.db.models import Sum
from django.test import TestCase

from ex.models import Symbol, Depo, LimitOrder, AbstractOrder
from services.transaction_service import resolve_order


class TestSymbol(TestCase):
    def test_bid_ask_count_property(self):
        ticker = 'tckr'
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker+'fn')
        maker_depo = Depo.objects.create(start_equity=10000)
        lo1 = LimitOrder(initiator=maker_depo, symbol=symbol,
                        dir=AbstractOrder.OrderDirection.BUY, price=500, quantity=5)
        lo2 = LimitOrder(initiator=maker_depo, symbol=symbol,
                        dir=AbstractOrder.OrderDirection.SELL, price=501, quantity=3)
        lo1.save()
        lo2.save()
        resolve_order(lo1)
        resolve_order(lo2)
        self.assertEqual(symbol.bid_count, 5)
        self.assertEqual(symbol.ask_count, 3)