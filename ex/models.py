from random import random
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import PositiveIntegerField, CharField, IntegerField, DateTimeField, \
    OneToOneField, F, ForeignKey, CASCADE, DO_NOTHING, DecimalField, BooleanField, Choices, TextChoices, FloatField, \
    Sum

MAX_DIGITS = 15
DECIMAL_PLACES = 2
MAX_TICKER_LENGTH = 4

class Depo(models.Model):
    @property
    def free_equity(self):
        positions = Position.objects.select_related('depo').filter(depo=self)
        return self.current_equity - sum([p.equity for p in positions]) - self.open_orders_equity

    @property
    def open_orders_equity(self):
        return (LimitOrder.objects.select_related('initiator').
                filter(initiator=self, status=AbstractOrder.OrderStatus.PLACED).
                aggregate(total_equity=Sum(F('quantity') * F('price')))['total_equity'] or 0)


    def save(self, *args, **kwargs) -> None:
        if self.current_equity is None:
            self.current_equity = self.start_equity

        super().save(*args, **kwargs)
        if not self.is_init:
            [Position.objects.create(depo=self, symbol=s) for s in
             Symbol.objects.all()]
            self.risk_rate = random()
            self.is_init = True

    user = OneToOneField(User, on_delete=CASCADE, null=True)
    risk_rate = FloatField(default=0)
    start_equity = FloatField(default=0)
    current_equity = FloatField(null=True)
    is_algo = BooleanField(default=False)
    is_init = BooleanField(default=False) # FIXME ultra mega cringe?


class Symbol(models.Model):
    """conatins info about stock, currency and others intstruments"""

    @property
    def bid_count(self):
        return (LimitOrder.objects.filter(dir=AbstractOrder.OrderDirection.BUY,
                                          status=AbstractOrder.OrderStatus.PLACED,
                                          symbol=self).
                aggregate(Sum('quantity'))['quantity__sum'] or 0)
    @property
    def ask_count(self):
        return (LimitOrder.objects.filter(dir=AbstractOrder.OrderDirection.SELL,
                                          status=AbstractOrder.OrderStatus.PLACED,
                                          symbol=self).
                aggregate(Sum('quantity'))['quantity__sum'] or 0)

    @property
    def volume(self):
        pass


    ticker = CharField(max_length=MAX_TICKER_LENGTH, unique=True)
    full_name = CharField(max_length=20, unique=True)
    best_bid = PositiveIntegerField(default=0)
    best_ask = PositiveIntegerField(default=2147483647) # max int for psql


class AbstractOrder(models.Model):
    class OrderDirection(models.TextChoices):
        BUY = 'BUY'
        SELL = 'SELL'
    class OrderStatus(models.TextChoices):
        INITIATED = "INITIATED",
        PLACED = "PLACED",
        FILLED = "FILLED",
        REJECTED = "REJECTED"
        ERROR = "ERROR"


    initiator = ForeignKey(Depo, on_delete=CASCADE)
    dir = CharField(choices=OrderDirection)
    datetime = DateTimeField(auto_now=True)
    quantity = PositiveIntegerField()
    status = CharField(choices=OrderStatus, default=OrderStatus.INITIATED)
    symbol = ForeignKey(Symbol, on_delete=CASCADE)

    class Meta:
        abstract = True


class MarketOrder(AbstractOrder):
    pass


class LimitOrder(AbstractOrder):
    price = IntegerField()


class StopOrder(AbstractOrder):
    trigger_price = IntegerField()


class TakeOrder(AbstractOrder):
    trigger_price = IntegerField()


class TriggerOrder(AbstractOrder):
    limit_order = OneToOneField(LimitOrder, on_delete=models.CASCADE)


class Transaction(models.Model):
    """transaction can be only between LimitOrder(maker) and MarketOrder(taker)"""
    ticker = CharField(max_length=4)
    price = PositiveIntegerField(default=0)
    volume = PositiveIntegerField(default=0)
    datetime = DateTimeField(auto_now=True)
    maker_order = ForeignKey(LimitOrder, on_delete=DO_NOTHING)
    taker_content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    taker_object_id = models.PositiveIntegerField()
    taker_order = GenericForeignKey('taker_content_type', 'taker_object_id')




class Position(models.Model):
    def update_position(self, price, quantity_):
        try:
            self.average_price = ((self.average_price * self.quantity + price * quantity_)
                                  / (self.quantity + quantity_))
        except ZeroDivisionError:
            self.average_price = 0
        self.quantity += quantity_
        self.save()

    @property
    def sign(self):
        return 1 if self.quantity > 0 else -1

    @property
    def equity(self):
        return abs(self.quantity * self.average_price) + self.pnl

    @property
    def pnl(self):
        actual_price = self.symbol.best_bid if self.sign == 1 else self.symbol.best_ask
        #print(self.symbol.best_ask, self.symbol.best_bid)

        return self.quantity * actual_price - self.average_price * self.quantity

    symbol = ForeignKey(Symbol, on_delete=DO_NOTHING)
    depo = ForeignKey(Depo, on_delete=CASCADE)
    average_price = FloatField(default=0)
    quantity = IntegerField(default=0)

    def __str__(self):
        return (f"ticker: {self.symbol.ticker}\n"
                f"quantity: {self.quantity}\n"
                f"average price: {self.average_price}")