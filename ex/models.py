from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import (
    PositiveIntegerField,
    CharField,
    IntegerField,
    DateTimeField,
    OneToOneField,
    ForeignKey,
    CASCADE,
    DO_NOTHING,
    BooleanField,
    FloatField,
)


MAX_DIGITS = 15
DECIMAL_PLACES = 2
MAX_TICKER_LENGTH = 4


# FIXME добавить изменение депозита после закрытия позици
class Depo(models.Model):
    user = OneToOneField(User, on_delete=CASCADE, null=True)
    risk_rate = FloatField(default=0)
    start_equity = FloatField(default=0)
    current_equity = FloatField(null=True)
    is_algo = BooleanField(default=False)


class Symbol(models.Model):
    """conatins info about stock, currency and others intstruments"""

    ticker = CharField(max_length=MAX_TICKER_LENGTH, unique=True)
    full_name = CharField(max_length=20, unique=True)
    # best_bid = PositiveIntegerField(default=0)
    # best_ask = PositiveIntegerField(default=2147483647)  # max int for psql

    def __repr__(self):
        return f"{self.ticker}"

    def __str__(self):
        return f"{self.ticker}"


class AbstractOrder(models.Model):
    class OrderDirection(models.TextChoices):
        BUY = "BUY"
        SELL = "SELL"

    class OrderStatus(models.TextChoices):
        INITIATED = ("INITIATED",)
        PLACED = ("PLACED",)
        FILLED = ("FILLED",)
        REJECTED = "REJECTED"
        CANCELED = "CANCELED"
        ERROR = "ERROR"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.is_init:
            self.initial_quantity = self.quantity
            self.is_init = True
        #print(self.quantity, self.initial_quantity)
        super().save(*args, **kwargs)

    initiator = ForeignKey(Depo, on_delete=CASCADE)
    direction = CharField(choices=OrderDirection)
    datetime = DateTimeField(auto_now=True)
    quantity = PositiveIntegerField()
    initial_quantity = PositiveIntegerField(default=0)
    status = CharField(choices=OrderStatus, default=OrderStatus.INITIATED)
    symbol = ForeignKey(Symbol, on_delete=CASCADE)
    is_init = BooleanField(default=False)  # FIXME ultra mega cringe?


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
    taker_order = GenericForeignKey("taker_content_type", "taker_object_id")


class Position(models.Model):
    def update_position(self, price, quantity_):
        try:
            self.average_price = (
                self.average_price * self.quantity + price * quantity_
            ) / (self.quantity + quantity_)
        except ZeroDivisionError:
            self.average_price = 0
        self.quantity += quantity_
        self.save()

    @property
    def sign(self):
        return 1 if self.quantity > 0 else -1

    symbol = ForeignKey(Symbol, on_delete=DO_NOTHING)
    depo = ForeignKey(Depo, on_delete=CASCADE)
    average_price = FloatField(default=0)
    quantity = IntegerField(default=0)

    def __str__(self):
        return (
            f"ticker: {self.symbol.ticker}\n"
            f"quantity: {self.quantity}\n"
            f"average price: {self.average_price}"
        )
