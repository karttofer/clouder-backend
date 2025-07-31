import random
from datetime import datetime


def generate_4_digit_pin():
    pin = random.randint(1000, 9999)
    return pin