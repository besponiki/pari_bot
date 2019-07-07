from mongoengine import *


class User(Document):
    user_id = IntField(required=True, unique=True)
    username = StringField()
    edit_message_id = IntField()

    first_name = StringField()
    last_name = StringField()

    state = StringField(max_length=50)
    user_lang = StringField(default='rus')

    balance = FloatField(default=0.0)

    referrals_count = IntField(default=0)
    parent_referral_user_id = StringField()
    referrals_users_ids = ListField(StringField())
    referrals_users_second_level_ids = ListField(StringField())

    all_bets_count = IntField(default=0)
    glodal_balance = FloatField(default=0)

    current_bets_count = IntField(default=0)
    current_bets_balance = FloatField(default=0)

    earn_from_referrals = FloatField(default=0.0)
    refund_sum = FloatField()
    is_first_start = BooleanField(default=True)
    is_up_bet = BooleanField()
    add_money = DictField()
    is_notification_active = BooleanField(default=True)
    is_blocked = BooleanField(default=False)

    def referrals_users(self):
        result = list()

        for user_id in self.referrals_users_ids:
            user: User = User.objects(user_id=user_id).first()

            if user:
                result.append(user)

        return result

    def second_level_referrals_users(self):
        result = list()

        for user_id in self.referrals_users_second_level_ids:
            user: User = User.objects(user_id=user_id).first()

            if user:
                result.append(user)

        return result

    def parent_referral_user(self):
        user = User.objects(user_id=self.parent_referral_user_id).first()

        return user
