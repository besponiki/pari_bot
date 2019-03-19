from mongoengine import *


class Refund(Document):
    data = StringField()
    user_id = IntField()
    username = StringField()
    paid_off = StringField(default="not")
    first_name = StringField()
    last_name = StringField()
    sum = IntField()
    wallet = StringField()
    payed = BooleanField(default=False)
