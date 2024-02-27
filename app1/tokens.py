from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models.query import QuerySet
from .models import *


class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (str(user.username) + str(timestamp))

custom_token_generator = CustomTokenGenerator()
 # Handle the case where user is None or queryset is empty





