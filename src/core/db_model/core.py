from mongoengine import *

from .message import Message


class Core(Document):
    random = BooleanField(db_field='random', default=True)
    messages = ListField(db_field='messages', field=ReferenceField(Message), default=list())
    edit_massage_ids = ListField()
    edit_massage_rus = StringField()
    edit_massage_eng = StringField()
    api_key = StringField()
    secret_key = StringField()

    pari_interval_in_minutes = IntField(default=120)
    pari_period_in_minutes = IntField(default=70)
    intermedia_period_1_info = IntField(default=5)
    intermedia_period_2_info = IntField(default=5)
    current_open_pari_bet_date = StringField()


    current_open_pari_time = DateTimeField()
    current_open_pari_price = FloatField()
    current_open_pari_bet_tag = IntField(default=0)
    additional_open_pari_bet_tag = IntField(default=0)
    current_open_pari_members = IntField(default=0)

    current_open_pari_members_up = IntField(default=0)
    current_open_pari_members_down = IntField(default=0)


    current_open_pari_sum_up_balance = FloatField(default=0.0)
    current_open_pari_sum_down_balance = FloatField(default=0.0)


    current_open_pari_virtual_up_sum_balance = FloatField(default=0.0)
    current_open_pari_virtual_down_sum_balance = FloatField(default=0.0)
    current_open_pari_virtual_members_up = IntField(default=0)
    current_open_pari_virtual_members_down = IntField(default=0)


    profit_percent = IntField(default=60)

    fee_username = StringField(default='')

    referral_bonus_price = FloatField(default=0.00004)
    referral_bonus_2_price = FloatField(default=0.00002)

    min_bet_size = FloatField(default=0.0004)

    main_btc_address = StringField()

    channel_link = IntField()

    link_1 = StringField()
    link_2 = StringField()

    txid_for_check = ListField()
    used_txid = ListField()
    ref1_percent = IntField()
    ref2_percent = IntField()