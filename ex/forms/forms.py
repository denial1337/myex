from django import forms


class MarketOrderForm(forms.Form):
    market_order_quantity = forms.IntegerField(label="Количество")


class LimitOrderForm(forms.Form):
    limit_order_quantity = forms.IntegerField(label="Количество")
    limit_order_price = forms.IntegerField(label="Цена")


class LimitOrderFormManager:
    form = LimitOrderForm


class MarketOrderFormManager:
    form = MarketOrderForm
