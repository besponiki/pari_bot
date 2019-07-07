from mongoengine import *
from .pari_bet import PariBet
from ...tg_bot.db_model.user import User

class CoreHistory(Document):
    pari_bet_tag = IntField(default=0)
    open_pari_date = StringField()
    open_pari_members = IntField(default=0)
    open_pari_balance = FloatField(default=0)
    open_pari_up_balance = FloatField(default=0)
    open_pari_down_balance = FloatField(default=0)
    win_side = BooleanField()
    commision_balance = FloatField(default=0)
    open_pari_virtual_up_sum_balance = FloatField(default=0)
    open_pari_virtual_down_sum_balance = FloatField(default=0)
    open_pari_virtual_members_up = FloatField(default=0)
    open_pari_virtual_members_down = FloatField(default=0)
    bets = DictField()

    def users_coef(self):
        data = dict()
        for user in User.objects():
            all_prices = 0
            bets = PariBet.objects(Q(user_id=user.user_id)&Q(tag=self.pari_bet_tag))
            if len(bets) != 0:
                for bet in bets:
                    all_prices += bet.victory_result
                    print(all_prices)
            if all_prices:
                data[str(user.user_id)] = str(all_prices/self.open_pari_balance * 100) + ' %'
        return data



