from mongoengine import *


class PariBet(Document):
    tag = LongField()
    is_up = BooleanField()
    balance = FloatField()
    user_id = IntField()
    victory_result = FloatField(default=0)
