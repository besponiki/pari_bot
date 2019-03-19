from mongoengine import *


class Message(Document):
    language = StringField(db_field='language', default='rus')
    text = StringField(db_field='text', null=True)
    user_ids = ListField(StringField())
    edit_message_ids = ListField(StringField())
    data = StringField()


class EditMessage(Document):
    edit_mailing = DictField()
    text = StringField()
    data = StringField()


class EditMessageEng(Document):
    edit_mailing = DictField()
    text = StringField()
    data = StringField()
