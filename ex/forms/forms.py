from django import forms


class MarketOrderForm(forms.Form):
    quantity = forms.IntegerField(label='Количество')

class LimitOrderForm(forms.Form):
    quantity = forms.IntegerField(label='Количество')
    price = forms.IntegerField(label='Цена')

class LimitOrderFormManager:
    form = LimitOrderForm

class MarketOrderFormManager:
    form = MarketOrderForm
