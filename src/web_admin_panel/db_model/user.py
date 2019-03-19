from mongoengine import Document, StringField, FloatField


class User(Document):
    meta = {'collection': 'web_admin_user'}

    session_id = StringField(db_field='session_id')
    time_alive = FloatField(db_field='time_alive')

    login = StringField(db_field='login', unique=True)
    password = StringField(db_field='password')
