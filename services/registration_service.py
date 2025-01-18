from django.contrib.auth.models import User

from ex.models import Depo, Symbol, Position

INIT_MONEY = 100_000


def create_depo_for_new_user(user: User) -> None:
    depo = Depo.objects.create(
        start_equity=INIT_MONEY,
        current_equity=INIT_MONEY,
        user=user,
    )
    symbols = Symbol.objects.all()
    for sym in symbols:
        Position.objects.create(
            symbol=sym,
            depo=depo
        )
