from mongoengine import *


class Question(Document):
    data = StringField()
    text = StringField()
    # user = ReferenceField('User')
    user_name = StringField()
    user_id = IntField()
    first_name = StringField()
    last_name = StringField()
    status = StringField(default="Не отвечено")
