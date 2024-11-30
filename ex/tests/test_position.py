#from unittest import TestCase
from django.test import TestCase
from ex.models import Position, Symbol, Depo, LimitOrder, AbstractOrder, MarketOrder, Transaction
from services.transaction_service import resolve_order, is_valid_market_order, \
    get_position_by_order, make_market_transaction


class TestDepo(TestCase):
    def test_depo_creation(self):
        tickers = ['t1','t2','t3']
        [Symbol.objects.create(ticker=t, full_name=t+'fn') for t in tickers]
        depo = Depo.objects.create(start_equity=10000)

        self.assertEqual(depo.is_init, True)
        self.assertEqual(Position.objects.filter(depo=depo).count(), len(tickers))
        self.assertEqual(depo.start_equity, 10000)
        self.assertEqual(depo.free_equity, 10000)
        self.assertEqual(depo.current_equity, 10000)

    def test_position_getter_and_update(self):
        ticker = 'tpu'
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + 'fn')
        maker_depo = Depo.objects.create(start_equity=10000)
        taker_depo = Depo.objects.create(start_equity=10000)
        lo1 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                                        dir=AbstractOrder.OrderDirection.BUY,
                                        price=499, quantity=5)
        lo2 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                                        dir=AbstractOrder.OrderDirection.SELL,
                                        price=501, quantity=5)
        resolve_order(lo1)
        resolve_order(lo2)

        mo = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=2,
                                        dir=AbstractOrder.OrderDirection.SELL)

        #resolve_order(mo)
        pos = get_position_by_order(mo)
        pos.update_position(499, 2)

        self.assertEqual(pos.average_price, 499)
        self.assertEqual(pos.quantity, 2)

        pos.update_position(499, -2)
        self.assertEqual(pos.average_price, 0)
        self.assertEqual(pos.quantity, 0)

        pos.update_position(499, -2)
        self.assertEqual(pos.average_price, 499)
        self.assertEqual(pos.quantity, -2)


    # def test_pnl(self):
    #     ticker = 'tpnl'
    #     symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + 'fn')
    #     maker_depo = Depo.objects.create(start_equity=10000)
    #     taker_depo = Depo.objects.create(start_equity=10000)
    #     lo1 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
    #                                     dir=AbstractOrder.OrderDirection.BUY,
    #                                     price=499, quantity=5)
    #     lo2 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
    #                                     dir=AbstractOrder.OrderDirection.SELL,
    #                                     price=501, quantity=5)
    #     resolve_order(lo1)
    #     resolve_order(lo2)
    #
    #     mo_sell = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=2,
    #                                     dir=AbstractOrder.OrderDirection.SELL)
    #     resolve_order(mo_sell)
    #
    #
    #     pos = get_position_by_order(mo_sell)
    #     self.assertEqual(pos.symbol.best_ask, 501)
    #     self.assertEqual(pos.symbol.best_bid, 499)
    #     self.assertEqual(mo_sell.status, AbstractOrder.OrderStatus.FILLED)
    #     #print(pos)
    #     self.assertEqual(pos.pnl, -4)
    #
    #     lo3 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
    #                                 dir=AbstractOrder.OrderDirection.SELL,
    #                                 price=500, quantity=5)
    #     resolve_order(lo3)
    #     pos.refresh_from_db()
    #     #print(symbol.best_ask, symbol.best_bid)
    #     self.assertEqual(lo3.status, AbstractOrder.OrderStatus.PLACED)
    #     self.assertEqual(pos.pnl, -2)
    #
    #     mo_buy = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=1,
    #                                          dir=AbstractOrder.OrderDirection.BUY)
    #     resolve_order(mo_buy)
    #     pos = get_position_by_order(mo_buy)
    #     self.assertEqual(pos.average_price, 500)
    #     self.assertEqual(pos.quantity, 1)
    #     self.assertEqual(mo_buy.status, AbstractOrder.OrderStatus.FILLED)
    #     self.assertEqual(pos.pnl, -1)





    def test_transaction(self):
        ticker = 'ttrn'
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + 'fn')
        maker_depo = Depo.objects.create(start_equity=10000)
        taker_depo = Depo.objects.create(start_equity=10000)
        lo = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                                       dir=AbstractOrder.OrderDirection.BUY, price=500, quantity=5)
        mo = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=2,
                                        dir=AbstractOrder.OrderDirection.SELL)
        make_market_transaction(lo, mo)


    def test_market_deals(self):
        ticker = 'tpot'
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + 'fn')
        maker_depo = Depo.objects.create(start_equity=10000)
        taker_depo = Depo.objects.create(start_equity=10000)
        lo = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                        dir=AbstractOrder.OrderDirection.BUY, price=500, quantity=5)
        mo = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=2,
                         dir=AbstractOrder.OrderDirection.SELL)

        resolve_order(lo)
        self.assertEqual(lo.status, AbstractOrder.OrderStatus.PLACED)
        resolve_order(mo)
        lo = LimitOrder.objects.get(pk=lo.pk)
        self.assertEqual(mo.status, AbstractOrder.OrderStatus.FILLED)
        self.assertEqual(mo.quantity, 0)
        self.assertEqual(lo.status, AbstractOrder.OrderStatus.PLACED)
        self.assertEqual(lo.quantity, 3)

        LimitOrder.objects.all().delete()
        MarketOrder.objects.all().delete()
        Transaction.objects.all().delete()

        lo = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                        dir=AbstractOrder.OrderDirection.BUY, price=500, quantity=5)
        mo = MarketOrder.objects.create(initiator=taker_depo, symbol=symbol, quantity=5,
                          dir=AbstractOrder.OrderDirection.SELL)

        resolve_order(lo)
        self.assertEqual(lo.status, AbstractOrder.OrderStatus.PLACED)
        resolve_order(mo)
        lo = LimitOrder.objects.get(pk=lo.pk)

        self.assertEqual(mo.status, AbstractOrder.OrderStatus.FILLED)
        self.assertEqual(mo.quantity, 0)
        self.assertEqual(lo.status, AbstractOrder.OrderStatus.FILLED)
        self.assertEqual(lo.quantity, 0)


    def test_depo_free_equity(self):
        ticker = 'tsfe'
        symbol = Symbol.objects.create(ticker=ticker, full_name=ticker + 'fn')
        maker_depo = Depo.objects.create(start_equity=10000)
        lo = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                        dir=AbstractOrder.OrderDirection.BUY, price=500, quantity=5)
        resolve_order(lo)
        self.assertEqual(maker_depo.open_orders_equity, 2500)
        self.assertEqual(maker_depo.free_equity, 7500)

        lo2 = LimitOrder.objects.create(initiator=maker_depo, symbol=symbol,
                                       dir=AbstractOrder.OrderDirection.SELL, price=1000, quantity=5)
        resolve_order(lo2)
        self.assertEqual(maker_depo.open_orders_equity, 7500)
        self.assertEqual(maker_depo.free_equity, 2500)

