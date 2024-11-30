from django.contrib.auth.models import User

from ex.models import Depo


def create_depo_for_new_user(user : User):
    depo = Depo.objects.create(start_equity=10_000, user=user)
