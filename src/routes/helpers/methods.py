# Deps
import random
import re
from typing import List, Dict


def generate_4_digit_pin():
    pin = random.randint(1000, 9999)
    return pin


def is_valid_name(strName):
    if not isinstance(strName, str):
        return False
    if not strName.strip():
        return False

    if not re.fullmatch(r'^[A-Za-z0-9_]+$', strName.strip()):
        return False

    return True


def is_int_value(value):
    return isinstance(value, int)


def is_invalid_data(value: List[Dict]) -> bool:
    return value == [{}] or not value
