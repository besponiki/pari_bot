from mongoengine import *


class Text(Document):
    values = DictField(db_field='values', default=dict())
    tag = StringField(db_field='tag', required=True, null=False, unique=True)
