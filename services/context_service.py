import base64
import io
import urllib.parse

from ex.forms.forms import MarketOrderFormManager, LimitOrderFormManager
from services.order_book_service import get_order_book_by_ticker
from services.transaction_service import get_last_transactions
from matplotlib import pyplot as plt

def get_context_by_ticker(ticker):
    t = get_last_transactions(ticker)
    context = {
        'order_book': get_order_book_by_ticker(ticker),
        'transactions': t,
        'ticker' : ticker,
        'price' : [x['price'] for x in list(t.values('price'))[::-1]],
        'datetime' : [x['datetime'].strftime('%H:%M:%S %m.%d')  for x in list(t.values('datetime'))[::-1]], #list(range(len(t))), #
        'market_order_form' : MarketOrderFormManager.form,
        'limit_order_form'  : LimitOrderFormManager.form
    }
    return context


def get_chart_url(last_transactions):
    data = [x['price'] for x in list(last_transactions.values('price'))]
    plt.plot(data[::-1])
    buf = io.BytesIO()
    fig=plt.gcf()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    url = urllib.parse.quote(string)
    plt.clf()
    return url