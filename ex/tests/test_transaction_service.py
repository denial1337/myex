from django.test import TestCase

from ex.models import Symbol, Depo, LimitOrder, AbstractOrder, MarketOrder
from services.transaction_service import make_market_transaction, get_position_by_order


class TestTransactionService(TestCase):
    def setup(self):
        ticker = 'tupa'
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + 'fn')
        maker_depo = Depo.objects.create(start_equity=10000)
        taker_depo = Depo.objects.create(start_equity=10000)

    def test_update_positions_after_transaction(self):
        ticker = 'tupa'
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + 'fn')
        maker_depo = Depo.objects.create(start_equity=10000)
        taker_depo = Depo.objects.create(start_equity=10000)
        lo1 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                                        dir=AbstractOrder.OrderDirection.BUY, price=499, quantity=5)
        lo2 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                                        dir=AbstractOrder.OrderDirection.SELL, price=501, quantity=3)

        mo = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=1,
                                        dir=AbstractOrder.OrderDirection.BUY)
        make_market_transaction(lo2, mo)
        mo.refresh_from_db()
        lo2.refresh_from_db()


    def test_make_market_transaction(self):
        ticker = 'tmmt'
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + 'fn')
        maker_depo = Depo.objects.create(start_equity=10000)
        taker_depo = Depo.objects.create(start_equity=10000)
        lo1 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                                        dir=AbstractOrder.OrderDirection.BUY, price=499, quantity=5)
        lo2 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                                        dir=AbstractOrder.OrderDirection.SELL, price=501, quantity=3)

        mo = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=1,
                                        dir=AbstractOrder.OrderDirection.BUY)
        make_market_transaction(lo2, mo)
        mo.refresh_from_db()
        lo2.refresh_from_db()

        maker_pos = get_position_by_order(lo2)
        taker_pos = get_position_by_order(mo)

        self.assertEqual(maker_pos.quantity, -1)
        self.assertEqual(taker_pos.quantity, 1)

        mo2 = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=1,
                                        dir=AbstractOrder.OrderDirection.BUY)

        make_market_transaction(lo2, mo2)
        mo2.refresh_from_db()
        lo2.refresh_from_db()

        maker_pos = get_position_by_order(lo2)
        taker_pos = get_position_by_order(mo2)

        self.assertEqual(maker_pos.quantity, -2)
        self.assertEqual(taker_pos.quantity, 2)

        mo3 = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=2,
                                        dir=AbstractOrder.OrderDirection.SELL)

        make_market_transaction(lo1, mo3)
        mo3.refresh_from_db()
        lo1.refresh_from_db()

        maker_pos = get_position_by_order(lo1)
        taker_pos = get_position_by_order(mo3)

        self.assertEqual(maker_pos.quantity, 0)
        self.assertEqual(taker_pos.quantity, 0)










