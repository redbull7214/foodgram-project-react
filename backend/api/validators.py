import datetime as dt
import re
from django.core.exceptions import ValidationError
from rest_framework import serializers

def validate_username(value):
    if value.lower() == 'me':
        raise serializers.ValidationError(
            "Нельзя использовать 'me' в качестве username")
    regular = r'[\w.@+-]+'
    result = (re.split(regular, value))
    for symbol in result:
        if symbol:
            raise serializers.ValidationError(
                f"Нельзя использовать {symbol} в username"
            )
    return value