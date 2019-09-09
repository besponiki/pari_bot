import threading
import time
import schedule
import datetime
import base64
import requests
import smtplib
import imghdr
import os
import json
import re
from binance.client import Client

from telebot import types
from mongoengine.queryset.visitor import Q

from . import keyboards
from .state_handler import StateHandler
from .logger_settings import logger

from .db_model.user import User

from ..web_admin_panel.service import from_dublicate_to_str
from .. import config

from ..core.db_model.core import Core
from ..core.db_model.core_history import CoreHistory
from ..core.db_model.questions import Question
from ..core.db_model.message import Message, EditMessage, EditMessageEng
from ..core.db_model.text.text import Text
from ..core.db_model.refund import Refund
from ..core.db_model.pari_bet import PariBet

class BotStates(StateHandler):
    def __init__(self, bot):
        super(BotStates, self).__init__(bot)

        self._register_states([
            # all states
            self._start_state,
            self.main_menu_state,
            self.language_state,
            self.callback_state,
            self.add_funds_state,
            self.pari_state,
            self.cash_refund_state,
            self.enter_sum_state,
            self.enter_wallet_state,
            self.my_pari_state
        ])

        self._running = True

        core: Core = Core.objects.first()
        if not core:
            core = Core()
            core.save()

        self._client: Client = Client(core.api_key, core.secret_key)
        print(self._client.get_deposit_address(asset='BTC'))

        self._kill_scheduling_event = threading.Event()
        self._kill_mailing_event = threading.Event()
        self._kill_pari_event = threading.Event()
        self._kill_payment_check_event = threading.Event()

        pari_threading = threading.Thread(
            target=self._pari_thread,
            args=[core.pari_interval_in_minutes, core.pari_period_in_minutes,
                  core.intermedia_period_1_info, core.intermedia_period_2_info]
        )
        pari_threading.daemon = True
        pari_threading.start()

        mailing = threading.Thread(target=self._mailing)
        mailing.daemon = True
        mailing.start()

        payment_check_thread = threading.Thread(
            target=self._payment_check
        )
        payment_check_thread.daemon = True
        payment_check_thread.start()

    def __del__(self):
        self._running = False

        self._kill_mailing_event.set()
        self._kill_scheduling_event.set()
        self._kill_pari_event.set()
        self._kill_payment_check_event.set()

    def _payment_check(self):
        core: Core = Core.objects().first()
        if not core:
            core = Core()
            core.save()

        while self._running and not self._kill_payment_check_event.is_set():
            deposit_history = self._client.get_deposit_history(asset='BTC')

            if deposit_history.get('success', None):
                core.reload()
                tx_ids_info = core.txid_for_check

                for user_id, tx_id, date in tx_ids_info:
                    try:
                        for deposit in deposit_history.get('depositList'):
                            if deposit.get('txId') == tx_id:
                                user: User = User.objects(user_id=user_id).first()

                                if user:
                                    user.balance += deposit.get('amount')
                                    user.save()
                                    #referral_bonus
                                    if user.parent_referral_user_id:
                                        parent_user: User = User.objects(user_id=int(user.parent_referral_user_id)).first()
                                        parent_user.balance += core.referral_bonus_price
                                        parent_user.earn_from_referrals += core.referral_bonus_price
                                        parent_user.save()
                                        if parent_user.parent_referral_user_id:
                                            parent_user_2: User = User.objects(user_id=int(parent_user.parent_referral_user_id)).first()
                                            parent_user_2.balance += core.referral_bonus_2_price
                                            parent_user_2.earn_from_referrals += core.referral_bonus_2_price
                                            parent_user_2.save()

                                    core.update(push__used_txid=tx_id)
                                    core.reload()

                                    core.update(pull__txid_for_check=(user_id, tx_id,))
                                    core.reload()
                                    # user sender
                                    text = self.locale_text(user.user_lang, 'add_funds_user_inform_msg')
                                    text = text.format(str(deposit.get('amount')))
                                    self._bot.send_message(user.user_id, text)
                                    # admin sender
                                    chanel_link = core.channel_link
                                    text1 = self.locale_text(user.user_lang, 'add_funds_admin_inform_msg')
                                    text1 = text1.format(str(user.user_id), str(deposit.get('amount')))
                                    expectation_time = datetime.datetime.utcnow()
                                    times = expectation_time.strftime('%d/%m/%y %H:%M')
                                    user.add_money[str(times)] = str(deposit.get('amount'))
                                    user.save()
                                    self._bot.send_message(chanel_link, text1)
                                    # send notification to user and admin channel
                    except Exception as e:
                        print(e)
        time.sleep(10)

    # def _payment_checking(self):
    #     core: Core = Core.objects().first()
    #     if not core:
    #         core = Core()
    #         core.save()
    #
    #     while self._running and not self._kill_payment_check_event.is_set():
    #         deposit_history = self._client.get_deposit_history(asset='BTC')
    #
    #         if deposit_history.get('success', None):
    #             core.reload()
    #             tx_ids_info = core.txid_for_check
    #
    #             for user_id, tx_id, date in tx_ids_info:
    #                 try:
    #                     for deposit in deposit_history.get('depositList'):
    #                         if deposit.get('txId') == tx_id:
    #                             print('hi!!!')
    #                 except Exception as e:
    #                     print(e)
    #         else:
    #             user: User = User.objects(user_id=643575597).first()
    #
    #             if user:
    #                 user.balance += 100
    #                 user.save()
    #                 # referral_bonus
    #                 if user.parent_referral_user_id:
    #                     parent_user: User = User.objects(
    #                         user_id=int(user.parent_referral_user_id)).first()
    #                     parent_user.balance += core.referral_bonus_price
    #                     parent_user.earn_from_referrals += core.referral_bonus_price
    #                     parent_user.save()
    #                     if parent_user.parent_referral_user_id:
    #                         parent_user_2: User = User.objects(
    #                             user_id=int(parent_user.parent_referral_user_id)).first()
    #                         parent_user_2.balance += core.referral_bonus_2_price
    #                         parent_user_2.earn_from_referrals += core.referral_bonus_2_price
    #                         parent_user_2.save()
    #                 # user sender
    #                 text = self.locale_text(user.user_lang, 'add_funds_user_inform_msg')
    #                 text = text.format(10)
    #                 self._bot.send_message(user.user_id, text)
    #                 # admin sender
    #                 chanel_link = core.channel_link
    #                 text1 = self.locale_text(user.user_lang, 'add_funds_admin_inform_msg')
    #                 text1 = text1.format(str(user.user_id), str(10))
    #                 expectation_time = datetime.datetime.utcnow()
    #                 times = expectation_time.strftime('%d/%m/%y %H:%M')
    #                 user.add_money[str(times)] = str(10)
    #                 user.save()
    #                 self._bot.send_message(chanel_link, text1)
    #                 break
    #                 # send notification to user and admin channel


    def _pari_thread(self, pari_interval_in_minutes, pari_period_in_minutes,
                     intermedia_period_1_info, intermedia_period_2_info):
        minute = datetime.datetime.utcnow().minute
        wait_time = 50 - minute if 50 > minute else 110 - datetime.datetime.utcnow().minute

        time.sleep(wait_time * 60)
        self._binance_pari_start()
        schedule.every(pari_interval_in_minutes).minutes.do(self._binance_pari_start)
        # first intermedia msg
        time.sleep(intermedia_period_1_info * 60)
        self._intermegia_1_pari_info()
        schedule.every(pari_interval_in_minutes).minutes.do(self._intermegia_1_pari_info)
        # second intermedia msg
        time.sleep(intermedia_period_2_info * 60)
        self._intermegia_2_pari_info()
        schedule.every(pari_interval_in_minutes).minutes.do(self._intermegia_2_pari_info)
        time.sleep((pari_period_in_minutes - intermedia_period_1_info - intermedia_period_2_info) * 60)
        self._binance_pari_stop()
        schedule.every(pari_interval_in_minutes).minutes.do(self._binance_pari_stop)

        while self._running and not self._kill_pari_event.is_set():
            try:
                schedule.run_pending()
            except Exception as e:
                logger.exception(e)
            finally:
                time.sleep(60)

    def _intermegia_1_pari_info(self):
        core: Core = Core.objects.first()
        sum_pari_member = core.current_open_pari_members+\
                          core.current_open_pari_virtual_members_up+core.current_open_pari_virtual_members_down

        sum_pari = core.current_open_pari_sum_up_balance+\
                   core.current_open_pari_sum_down_balance+core.current_open_pari_virtual_up_sum_balance+\
                   core.current_open_pari_virtual_down_sum_balance

        for user in User.objects(Q(is_blocked=False) & Q(is_notification_active=True)):

            # noinspection PyBroadException
            try:
                user_lang = user.user_lang
                text = self.locale_text(user_lang, 'intermedia_1_pari_info_msg')
                text = text.format(
                    str(sum_pari_member),
                    str(sum_pari)
                )
                message = self._bot.send_message(
                    user.user_id, text, parse_mode="markdown")
                user.edit_message_id = message.message_id
                user.save()
            except:
                pass

    def _intermegia_2_pari_info(self):
        core: Core = Core.objects.first()

        sum_pari_member_up = core.current_open_pari_members_up+core.current_open_pari_virtual_members_up
        sum_pari_member_down = core.current_open_pari_members_down+core.current_open_pari_virtual_members_down

        sum_pari_up = core.current_open_pari_sum_up_balance+core.current_open_pari_virtual_up_sum_balance
        sum_pari_down = core.current_open_pari_sum_down_balance+core.current_open_pari_virtual_down_sum_balance

        for user in User.objects(Q(is_blocked=False) & Q(is_notification_active=True)):
            # noinspection PyBroadException
            try:
                user_lang = user.user_lang

                text = self.locale_text(user_lang, 'intermedia_2_pari_info_msg')

                text = text.format(
                    str(sum_pari_member_up),
                    str(sum_pari_up),
                    str(sum_pari_member_down),
                    str(sum_pari_down)
                )
                print(user.username)
                print(user.edit_message_id)
                self._bot.edit_message_text(text=text, message_id=user.edit_message_id, chat_id=user.user_id)
            except:
                pass

    def _binance_pari_start(self):
        core: Core = Core.objects.first()
        core.current_open_pari_bet_tag = core.additional_open_pari_bet_tag
        core.current_open_pari_virtual_up_sum_balance = 0
        core.current_open_pari_virtual_down_sum_balance = 0
        core.current_open_pari_virtual_members_up = 0
        core.current_open_pari_virtual_members_down = 0
        core.current_open_pari_bet_date = str(datetime.datetime.utcnow())
        core.current_open_pari_time = datetime.datetime.utcnow()
        core.save()
        expectation_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=core.pari_period_in_minutes, hours=3)

        info = self._client.get_aggregate_trades(symbol='BTCUSDT')[-1].get('p')

        info = str(info)
        info = info[0:info.index('.') + 2]
        for user in User.objects(Q(is_blocked=False) & Q(is_notification_active=True)):
            # noinspection PyBroadException
            try:
                user_lang = user.user_lang

                text = self.locale_text(user_lang, 'sender_msg')
                text = text.format(
                    info,
                    expectation_time.strftime('%d/%m/%y %H:%M')
                )
                self._bot.send_message(
                    user.user_id, text, parse_mode="markdown",
                    reply_markup=keyboards.up_down_keyboard(user_lang)
                )
            except:
                pass


    def _binance_pari_stop(self):
        info = self._client.get_aggregate_trades(symbol='BTCUSDT')[-1].get('p')

        core: Core = Core.objects.first()

        pari_bet_tag = core.current_open_pari_bet_tag

        is_up_win = True if float(info) > core.current_open_pari_price else False
        if is_up_win == True:
            lose_point = False
        else:
            lose_point = True


        win_pari_bets = PariBet.objects(Q(tag=pari_bet_tag) & Q(is_up=is_up_win))

        lose_pari_bets = PariBet.objects(Q(tag=pari_bet_tag) & Q(is_up=lose_point))

        if lose_pari_bets:

            for bet in lose_pari_bets:
                print(bet.user_id)
                lose_user = User.objects(user_id=bet.user_id).first()
                print(lose_user)
                text = self.locale_text(lose_user.user_lang, 'lose_touser_msg')
                text = text.format(bet.balance)
                self._bot.send_message(lose_user.user_id, text)

        # the biggest bet
        best_win_balance = 0.0
        win_balance = core.current_open_pari_sum_up_balance if is_up_win else core.current_open_pari_sum_down_balance  # winning bets
        full_balance = core.current_open_pari_sum_up_balance + core.current_open_pari_sum_down_balance# full balance
        destribute_balance = full_balance - win_balance  # loser money
        win_balance += core.current_open_pari_virtual_up_sum_balance if is_up_win else core.current_open_pari_virtual_down_sum_balance # + virtual
        destribute_balance += core.current_open_pari_virtual_down_sum_balance if is_up_win else core.current_open_pari_virtual_up_sum_balance
        full_percent_balance = destribute_balance * core.profit_percent / 100 #93% of loser money
        parent1_sum = destribute_balance * core.ref1_percent/100
        parent2_sum = destribute_balance * core.ref2_percent/100
        additional_percent_balance = parent1_sum + parent2_sum
        fee_percent_balance = destribute_balance - full_percent_balance - additional_percent_balance
        destribute_balance = destribute_balance - fee_percent_balance - additional_percent_balance #

        # add fee for main user
        fee_user: User = User.objects(username=core.fee_username).first()
        fee_user.balance += fee_percent_balance
        fee_user.save()

        for bet in win_pari_bets:
            print(win_balance)
            coefficient = bet.balance / win_balance #-(win_balance * core.profit_percent)
            parent1_balance = coefficient * parent1_sum
            parent2_balance = coefficient * parent2_sum
            user_win_balance = coefficient * destribute_balance # розприділяються бабки проігравших
            if user_win_balance + bet.balance - parent1_balance - parent2_balance > best_win_balance:
                best_win_balance = user_win_balance + bet.balance

            bet.victory_result += user_win_balance + bet.balance
            bet.save()
            user: User = User.objects(user_id=bet.user_id).first()
            user.balance += user_win_balance + bet.balance
            user.save()

            if user.parent_referral_user_id:
                parent_user = User.objects(user_id=user.parent_referral_user_id).first()
                parent_user.balance += parent1_balance
                parent_user.earn_from_referrals += parent1_balance
                parent_user.save()
                if parent_user.parent_referral_user_id:
                    parent_user2 = User.objects(user_id=parent_user.parent_referral_user_id).first()
                    parent_user2.balance += parent2_balance
                    parent_user2.earn_from_referrals += parent2_balance
                    parent_user2.save()
                else:
                    fee_user.balance += parent2_balance
                    fee_user.save()
            else:
                fee_user.balance += parent2_balance + parent1_balance
                fee_user.save()

            text = self.locale_text(user.user_lang, 'winning_touser_msg')
            text = text.format(user_win_balance + bet.balance)
            self._bot.send_message(user.user_id, text)

        info = str(info)
        info = info[0:info.index('.') + 2]
        if is_up_win:
            best_win_balance += core.current_open_pari_virtual_up_sum_balance
        else:
            best_win_balance += core.current_open_pari_virtual_down_sum_balance

        pari_bet = PariBet.objects(tag=core.current_open_pari_bet_tag)
        # start

        core_history: CoreHistory = CoreHistory()
        core_history.pari_bet_tag = core.current_open_pari_bet_tag
        core_history.open_pari_date = core.current_open_pari_bet_date
        core_history.open_pari_members = core.current_open_pari_members
        core_history.open_pari_balance = core.current_open_pari_sum_up_balance \
                                         + core.current_open_pari_sum_down_balance
        core_history.open_pari_up_balance = core.current_open_pari_sum_up_balance
        core_history.open_pari_down_balance = core.current_open_pari_sum_down_balance
        core_history.commision_balance = fee_percent_balance
        core_history.open_pari_virtual_up_sum_balance = core.current_open_pari_virtual_up_sum_balance
        core_history.open_pari_virtual_down_sum_balance = core.current_open_pari_virtual_down_sum_balance
        core_history.open_pari_virtual_members_up = core.current_open_pari_virtual_members_up
        core_history.open_pari_virtual_members_down = core.current_open_pari_virtual_members_down
        core_history.win_side = is_up_win
        for bet in pari_bet:
            core_history.bets = {str(id): {
                'balance': bet.balance,
                'is_up': bet.is_up,
                'user_id': bet.user_id
            }}
        core_history.save()
        core.current_open_pari_price = float(info)
        core.additional_open_pari_bet_tag = core.current_open_pari_bet_tag + 1
        core.current_open_pari_bet_tag = None
        core.current_open_pari_sum_up_balance = 0.0
        core.current_open_pari_sum_down_balance = 0.0
        core.current_open_pari_members = 0
        core.current_open_pari_members_up = 0
        core.current_open_pari_members_down = 0
        core.current_open_pari_bet_date = '--'
        core.save()

        # nullificatication
        core.current_open_pari_virtual_up_sum_balance = 0
        core.current_open_pari_virtual_down_sum_balance = 0
        core.current_open_pari_virtual_members_up = 0
        core.current_open_pari_virtual_members_down = 0
        core.save()
        # end
        for user in User.objects(Q(is_blocked=False) & Q(is_notification_active=True)):
            try:
                user_lang = user.user_lang
                text = self.locale_text(user_lang, 'stop_pari_msg')
                text = text.format(
                    info,
                    str(core.profit_percent),
                    str(best_win_balance),
                    str(core.pari_interval_in_minutes - core.pari_period_in_minutes)
                )
                self._bot.send_message(
                    user.user_id, text, parse_mode="markdown"
                )

            except Exception as e:
                logger.exception(e)

        for user in User.objects():
            user.current_bets_count = 0
            user.current_bets_balance = 0
            user.save()

    def _mailing(self):
        core: Core = Core.objects.first()

        if not core:
            core = Core()
            core.save()

        while self._running and not self._kill_mailing_event.is_set():
            if len(core.messages) != 0:
                message: Message = core.messages[0]
                try:
                    if message:
                        print(message.language)
                        users = User.objects(Q(user_lang=message.language) & Q(is_blocked=False))
                        if message.user_ids is None:
                            message.user_ids = []
                            message.save()
                        edit_mailing = dict()
                        for user in users:
                            try:
                                asd = self._bot.send_message(user.user_id, message.text, parse_mode='markdown')
                                core.edit_massage_id = asd.message_id
                                time.sleep(0.5)
                                edit_mailing[str(user.user_id)] = asd.message_id
                            except Exception as e:
                                print(e)
                        if message.language == 'rus':
                            edit: EditMessage = EditMessage()
                            edit.edit_mailing = edit_mailing
                            edit.text = message.text
                            data = datetime.datetime.now()
                            edit.data = str(data)
                            edit.save()
                        elif message.language == 'eng':
                            edit: EditMessageEng = EditMessageEng()
                            edit.edit_mailing = edit_mailing
                            data = datetime.datetime.now()
                            edit.data = str(data)
                            edit.text = message.text
                            edit.save()
                except Exception as e:
                    print(e)
                finally:
                    core.update(pop__messages=1)
                    core.reload()

            core.reload()
            time.sleep(5)

    def _start_state(self, message: types.Message, entry=False):
        user: User = User.objects(user_id=message.chat.id).first()

        if user.is_blocked:
            return None
        if message.text[7:]:
            user_parent_ids = self.find_parents_ids(message.text[7:])
            if user.user_id in user_parent_ids:
                self._go_to_state(message, 'language_state')
                return None

        if user.is_first_start == False:
            self._go_to_state(message, 'language_state')
            return None

        if user and not user.parent_referral_user_id and message.text[7:] and user.user_id != int(message.text[7:]):
            try:
                referral_user: User = User.objects(user_id=message.text[7:]).first()

                if referral_user:
                    user.parent_referral_user_id = str(referral_user.user_id)
                    user.save()

                    if user.referrals_users_ids is None:
                        user.referrals_users_ids = []
                        user.save()

                    referral_user.update(add_to_set__referrals_users_ids=str(user.user_id))

                    referral_user.reload()
                    referral_user.referrals_count += 1
                    referral_user.save()

                referral_user2: User = User.objects(user_id=referral_user.parent_referral_user_id).first()
                if referral_user2:
                    referral_user2.update(add_to_set__referrals_users_second_level_ids=str(user.user_id))

                    referral_user2.reload()
                    referral_user2.referrals_count += 1
                    referral_user2.save()

            except Exception as e:
                logger.exception(e)
        user.is_first_start = False
        user.save()
        self._go_to_state(message, 'language_state')

    def language_state(self, message, entry=False, call: types.CallbackQuery = None):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang
        if user.is_blocked:
            return None

        if entry:
            text = self.locale_text(user_lang, 'choose_lang_msg')
            self._bot.send_message(user.user_id, text,
                                   reply_markup=keyboards.choose_lang_keyboard(user_lang))

            user.state = 'main_menu_state'
            user.save()
        else:
            if call:
                if call.data == 'language_state_inline_button_1_option':
                    user.user_lang = 'rus'
                    user.save()
                    self._go_to_state(message, 'main_menu_state')
                elif call.data == 'language_state_inline_button_2_option':
                    user.user_lang = 'eng'
                    user.save()
                    self._go_to_state(message, 'main_menu_state')

    def main_menu_state(self, message, entry=False, call: types.CallbackQuery = None):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang

        if user.is_blocked:
            return None
        if entry:


            core: Core = Core.objects.first()
            if not core:
                core = Core()
                core.save()

            text1 = self.locale_text(user_lang, 'main_menu_msg1')
            text1 = text1.format(
                str(core.profit_percent),
                str(1 + core.profit_percent / 100)
            )
            text2 = self.locale_text(user_lang, 'main_menu_msg2')
            text2 = text2.format(
                from_dublicate_to_str(core.referral_bonus_price)
            )
            text3 = self.locale_text(user_lang, 'main_menu_msg3')
            self._bot.send_message(user.user_id, text1)
            self._bot.send_message(user.user_id, text2)
            self._bot.send_message(user.user_id, text3,
                                   reply_markup=keyboards.main_menu_keyboard(user_lang))

            # self._binance_pari_stop()
            # self._binance_pari_start()
            # self._intermegia_1_pari_info()
            # self._intermegia_2_pari_info()
            # self._payment_checking()
        #


        else:
            if message.text == self.locale_text(user_lang, 'add_funds'):
                self._go_to_state(message, 'add_funds_state')
            elif message.text == self.locale_text(user_lang, 'pari'):
                self._go_to_state(message, 'my_pari_state')
            elif message.text == self.locale_text(user_lang, 'cash_refund'):
                self._go_to_state(message, 'cash_refund_state')
            elif message.text == self.locale_text(user_lang, 'my_balance'):
                text = self.locale_text(user_lang, 'my_balance_msg')
                text = text.format(user.balance)
                self._bot.send_message(user.user_id, text, parse_mode='markdown')
            elif message.text == self.locale_text(user_lang, 'addition'):
                text = self.locale_text(user_lang, 'choose_action')
                self._bot.send_message(user.user_id, text,
                                       reply_markup=keyboards.additional_keyboard(
                                           user_lang, user.is_notification_active
                                       ))
            elif call.data == 'main_menu_state_inline_button_1_option':
                # ask question
                self._go_to_state(message, 'callback_state')
            elif call.data == 'main_menu_state_inline_button_2_option':
                core: Core = Core.objects.first()
                if not core:
                    core = Core()
                    core.save()

                # referrals
                text = self.locale_text(user_lang, 'referrals_link_msg')
                text = text.format(
                    user.referrals_count,
                    user.earn_from_referrals,
                    self._ref_link(user.user_id),
                    str(from_dublicate_to_str(core.referral_bonus_price))
                )
                self._bot.send_message(user.user_id, text,
                                       parse_mode='markdown')
            elif call.data == 'main_menu_state_inline_button_3_option':
                # change_language
                text = self.locale_text(user_lang, 'additional_choose_lang_msg')
                self._bot.send_message(user.user_id, text,
                                       reply_markup=keyboards.additional_lang_keyboard(user_lang))

            elif call.data == 'main_menu_state_inline_button_5_option':
                user.user_lang = 'rus'
                user.save()

                text = self.locale_text(user_lang, 'successfully_change_lang_msg')
                self._bot.send_message(user.user_id, text, parse_mode='markdown')
            elif call.data == 'main_menu_state_inline_button_6_option':
                user.user_lang = 'eng'
                user.save()

                text = self.locale_text(user_lang, 'successfully_change_lang_msg')
                self._bot.send_message(user.user_id, text, parse_mode='markdown')
            elif call.data == 'main_menu_state_inline_button_4_option':
                # faq
                core: Core = Core.objects.first()
                if not core:
                    core = Core()
                    core.save()

                text = self.locale_text(user_lang, 'faq_q_msg')
                text = text.format(
                    core.link_1,
                    core.link_2
                )
                self._bot.send_message(user.user_id, text, parse_mode='markdown')
            elif call.data == 'main_menu_state_inline_button_7_option':
                user.is_notification_active = True
                user.save()

                self._bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=keyboards.additional_keyboard(user_lang, user.is_notification_active)
                )
            elif call.data == 'main_menu_state_inline_button_8_option':
                user.is_notification_active = False
                user.save()

                self._bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=keyboards.additional_keyboard(user_lang, user.is_notification_active)
                )
            else:
                pass

    def callback_state(self, message, entry=False, ):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang
        core: Core = Core.objects.first()
        if entry:
            text = self.locale_text(user_lang, 'pls_enter_quest_msg')
            self._bot.send_message(user.user_id, text)
        else:
            if message:
                if message.text == self.locale_text(user_lang, 'add_funds') or \
                        message.text == self.locale_text(user_lang, 'pari') or \
                        message.text == self.locale_text(user_lang, 'cash_refund') or \
                        message.text == self.locale_text(user_lang, 'my_balance') or \
                        message.text == self.locale_text(user_lang, 'addition'):
                    self._go_to_state(message, 'main_menu_state', entry=False)
                else:
                    question = Question()
                    data = datetime.datetime.now()
                    question.data = str(data)
                    question.text = message.text
                    question.user_id = user.user_id
                    question.user_name = user.username
                    question.first_name = user.first_name
                    question.last_name = user.last_name
                    question.save()
                    text = self.locale_text(user_lang, 'ask_question_answer_mag')
                    self._bot.send_message(user.user_id, text)
                    chanel_link = core.channel_link
                    text = self.locale_text(user_lang, 'question_to_admin_msg')
                    text = text.format(user.user_id, question.text)
                    self._bot.send_message(chanel_link, text)


    def add_funds_state(self, message, entry=False, call: types.CallbackQuery = None):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang
        if entry:
            text = self.locale_text(user_lang, 'choose_add_funds_msg')
            self._bot.send_message(user.user_id, text,
                                   reply_markup=keyboards.add_funds_keyboard(user_lang))
            user.state = 'main_menu_state'
            user.save()
        else:
            if call:
                if call.data == 'add_funds_state_inline_button_1_option':
                    core: Core = Core.objects().first()

                    if not core:
                        core = Core()
                        core.save()

                    text = self.locale_text(user_lang, 'apply_add_funds_msg')
                    self._bot.send_message(user.user_id, text, parse_mode='markdown',
                                           reply_markup=keyboards.apply_funds_keyboard(user_lang))

                    text_1 = str(core.main_btc_address)
                    self._bot.send_message(message.chat.id, text_1, parse_mode='markdown')
                elif call.data == 'add_funds_state_inline_button_2_option':
                    text = self.locale_text(user_lang, 'pls_enter_txid_msg')
                    self._bot.send_message(user.user_id, text, parse_mode='markdown')
            elif message.text == self.locale_text(user_lang, 'add_funds') \
                    or message.text == self.locale_text(user_lang, 'pari') \
                    or message.text == self.locale_text(user_lang, 'cash_refund') \
                    or message.text == self.locale_text(user_lang, 'my_balance') \
                    or message.text == self.locale_text(user_lang, 'addition'):
                self._go_to_state(message, 'main_menu_state', entry=False)
            else:
                txid = message.text

                core: Core = Core.objects().first()

                if not core:
                    core = Core()
                    core.save()

                if txid not in core.used_txid:
                    date = datetime.datetime.now()
                    core.update(push__txid_for_check=(user.user_id, txid, str(date)))
                    core.reload()

                text = self.locale_text(user_lang, 'thanks_txid_msg')
                self._bot.send_message(user.user_id, text)

    def my_pari_state(self, message, entry=False):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang

        if entry:
            core: Core = Core.objects.first()
            pari_tag = core.current_open_pari_bet_tag
            pari_bets = PariBet.objects(Q(tag=pari_tag) & Q(user_id=user.user_id))
            pari_bets_2 = PariBet.objects(user=user)
            # user.all_bets_count += pari_bets_2.count()
            # global_balance = user.glodal_balance
            # for bet in pari_bets_2:
            #     global_balance += bet.balance
            # user.glodal_balance = global_balance

            # all_bets_count = 0
            # all_bets_count += pari_bets_2.count()
            # global_balance = 0
            # for bet in pari_bets_2:
            #     global_balance += bet.balance


            addition_text = ''
            print(pari_bets.count())
            if pari_bets.count() > 0:
                for bet in pari_bets:
                    pari_information_2_msg = self.locale_text(user_lang, 'pari_information_2_msg')
                    addition_text += pari_information_2_msg.format(
                        str(bet.balance),
                        self.locale_text(user_lang, 'up_button_msg') if bet.is_up
                        else self.locale_text(user_lang, 'down_button_msg')
                    ) + ' \n\n'
            else:
                addition_text = self.locale_text(user_lang, 'no_pari_msg')

            text = self.locale_text(user_lang, 'pari_information_msg')
            text = text.format(str(user.all_bets_count), str(user.glodal_balance), addition_text)
            self._bot.send_message(
                user.user_id, text,
                parse_mode='Markdown'
            )

            user.state = 'main_menu_state'
            user.save()

    def pari_state(self, message, entry=False, call: types.CallbackQuery = None):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang
        core = Core.objects().first()

        if entry:
            core: Core = Core.objects.first()
            expectation_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=core.pari_period_in_minutes)
            info = self._client.get_aggregate_trades(symbol='BTCUSDT')[-1].get('p')
            info = str(info)
            info = info[0:info.index('.')+2]
            text = self.locale_text(user_lang, 'sender_msg')
            text = text.format(
                info,
                expectation_time.strftime('%d/%m/%y %H:%M')
            )

            self._bot.send_message(
                user.user_id, text, parse_mode="markdown",
                reply_markup=keyboards.up_down_keyboard(user_lang)
            )

            user.state = 'main_menu_state'
            user.save()
        else:
            if call:
                if call.data == 'pari_state_inline_button_1_option':
                    current_time = datetime.datetime.utcnow()
                    time_delta = datetime.timedelta(minutes=10)
                    if core.current_open_pari_time + time_delta > current_time:


                        text = self.locale_text(user_lang, 'enter_bet_sum_msg')

                        core: Core = Core.objects.first()
                        text = text.format(
                            str(core.min_bet_size)
                        )

                        self._bot.send_message(
                            user.user_id, text, parse_mode="markdown",
                            reply_markup=keyboards.main_menu_keyboard(user_lang)
                        )

                        user.is_up_bet = False
                        user.save()
                    else:
                        text = self.locale_text(user.user_lang, 'stop_bets_interval_msg')
                        self._bot.send_message(user.user_id, text)
                elif call.data == 'pari_state_inline_button_2_option':
                    current_time = datetime.datetime.utcnow()
                    time_delta = datetime.timedelta(minutes=10)
                    if core.current_open_pari_time + time_delta > current_time:
                        text = self.locale_text(user_lang, 'enter_bet_sum_msg')

                        core: Core = Core.objects.first()
                        text = text.format(
                            str(core.min_bet_size)
                        )

                        self._bot.send_message(
                            user.user_id, text, parse_mode="markdown",
                            reply_markup=keyboards.main_menu_keyboard(user_lang)
                        )

                        user.is_up_bet = True
                        user.save()
                    else:
                        text = self.locale_text(user.user_lang, 'stop_bets_interval_msg')
                        self._bot.send_message(user.user_id, text)

            else:
                if message.text == self.locale_text(user_lang, 'add_funds') \
                        or message.text == self.locale_text(user_lang, 'pari') \
                        or message.text == self.locale_text(user_lang, 'cash_refund') \
                        or message.text == self.locale_text(user_lang, 'my_balance') \
                        or message.text == self.locale_text(user_lang, 'addition'):
                    self._go_to_state(message, 'main_menu_state', entry=False)
                else:
                    text = message.text.replace(' ', '').replace(',', '.').lower()

                    # noinspection PyBroadException
                    try:
                        float_value = float(text)
                    except Exception:
                        if text.find('btc') != -1:
                            float_value = text[:text.find('btc')]

                            # noinspection PyBroadException
                            try:
                                float_value = float(float_value)
                            except Exception:
                                text = self.locale_text(user_lang, 'not_valid_bet_sum_msg')
                                self._bot.send_message(
                                    user.user_id, text, parse_mode="markdown",
                                    reply_markup=keyboards.main_menu_keyboard(user_lang)
                                )
                                return None
                        else:
                            text = self.locale_text(user_lang, 'not_valid_bet_sum_msg')
                            self._bot.send_message(
                                user.user_id, text, parse_mode="markdown",
                                reply_markup=keyboards.main_menu_keyboard(user_lang)
                            )
                            return None
                    if float_value < core.min_bet_size:
                        text = self.locale_text(user_lang, 'small_sum')
                        self._bot.send_message(user.user_id, text, parse_mode="markdown",
                                reply_markup=keyboards.main_menu_keyboard(user_lang))
                    else:
                        if 0 < float_value <= user.balance:
                            user.balance -= float_value
                            user.current_bets_balance += float_value
                            user.current_bets_count += 1
                            user.all_bets_count += 1
                            user.glodal_balance += float_value
                            user.save()

                            core: Core = Core.objects.first()

                            bet: PariBet = PariBet()

                            bet.tag = core.current_open_pari_bet_tag
                            bet.user_id = user.user_id
                            bet.is_up = user.is_up_bet
                            bet.balance = float_value
                            bet.save()



                            core: Core = Core.objects.first()

                            if PariBet.objects(Q(tag=core.current_open_pari_bet_tag) & Q(user_id=bet.user_id)).count() == 1:
                                core.current_open_pari_members += 1
                            if bet.is_up:
                                core.current_open_pari_members_up += 1
                                core.save()
                            else:
                                core.current_open_pari_members_down += 1
                                core.save()

                            if bet.is_up:
                                core.current_open_pari_sum_up_balance += float_value
                            else:
                                core.current_open_pari_sum_down_balance += float_value

                            core.save()
                            print(user)
                            print(user_lang)






                            # розсилка в канал
                            chanel_link = core.channel_link
                            # chanel_link = 0-int(chanel_link)
                            text = self.locale_text(user_lang, 'chanel_msg')
                            text = text.format(core.current_open_pari_bet_tag, bet.balance, user.user_id)
                            self._bot.send_message(chanel_link, text)


                            text = self.locale_text(user_lang, 'bet_success_msg')
                            self._bot.send_message(
                                user.user_id, text, parse_mode="markdown",
                                reply_markup=keyboards.main_menu_keyboard(user_lang)
                            )

                            user.state = 'main_menu_state'
                            user.save()
                        else:
                            text = self.locale_text(user_lang, 'no_enough_coin_msg')
                            self._bot.send_message(
                                user.user_id, text, parse_mode="markdown",
                                reply_markup=keyboards.main_menu_keyboard(user_lang)
                            )
                            return None

    def cash_refund_state(self, message, entry=False, call: types.CallbackQuery = None):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang
        if entry:
            text = self.locale_text(user_lang, 'check_currency_msg')
            self._bot.send_message(user.user_id, text,
                                   reply_markup=keyboards.cash_refund_keyboard(user_lang))
            user.state = 'main_menu_state'
            user.save()
        else:
            if call:
                if call.data == 'cash_refund_state_inline_button_1_option':
                    self._go_to_state(message, 'enter_sum_state')

    def enter_sum_state(self, message, entry=False, call: types.CallbackQuery = None):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang
        if entry:
            text = self.locale_text(user_lang, 'cash_refund_enter_msg')
            self._bot.send_message(user.user_id, text)
        else:
            if message.text == self.locale_text(user_lang, 'add_funds') \
                    or message.text == self.locale_text(user_lang, 'pari') \
                    or message.text == self.locale_text(user_lang, 'cash_refund') \
                    or message.text == self.locale_text(user_lang, 'my_balance') \
                    or message.text == self.locale_text(user_lang, 'addition'):
                self._go_to_state(message, 'main_menu_state', entry=False)
            else:
                try:
                    value = float(message.text.replace(',', '.'))

                    if user.balance >= value > 0:
                        user.refund_sum = value
                        user.save()

                        self._go_to_state(message, 'enter_wallet_state')
                    else:
                        text = self.locale_text(user_lang, 'not_enough_money_msg')
                        self._bot.send_message(user.user_id, text)
                except:
                    text = self.locale_text(user_lang, 'invalid_enterance_msg')
                    self._bot.send_message(user.user_id, text)

    def enter_wallet_state(self, message, entry=False, call: types.CallbackQuery = None):
        user: User = User.objects(user_id=message.chat.id).first()
        user_lang = user.user_lang
        core = Core.objects.first()
        if entry:
            text = self.locale_text(user_lang, 'enter_wallet_msg')
            self._bot.send_message(user.user_id, text)
        else:
            if message.text == self.locale_text(user_lang, 'add_funds') \
                    or message.text == self.locale_text(user_lang, 'pari') \
                    or message.text == self.locale_text(user_lang, 'cash_refund') \
                    or message.text == self.locale_text(user_lang, 'my_balance') \
                    or message.text == self.locale_text(user_lang, 'addition'):
                self._go_to_state(message, 'main_menu_state', entry=False)
            else:
                refund = Refund()
                data = datetime.datetime.now()
                refund.data = str(data)
                refund.sum = user.refund_sum
                refund.wallet = message.text
                refund.user_id = user.user_id
                refund.username = user.username
                refund.first_name = user.first_name
                refund.last_name = user.last_name
                refund.save()
                user.refund_sum = None
                user.save()
                text = self.locale_text(user_lang, 'mail_moderating_msg')
                self._bot.send_message(user.user_id, text)

                chanel_link = core.channel_link
                text = self.locale_text(user_lang, 'cash_refund_admin_msg')
                text = text.format(user.user_id, refund.sum)
                self._bot.send_message(chanel_link, text)

                user.state = 'main_menu_state'
                user.save()



    @staticmethod
    def locale_text(lang, tag):
        if not lang or not tag:
            return None

        text = Text.objects(tag=tag).first()

        if not text:
            return None

        return text.values.get(lang)

    @staticmethod
    def user_clear(user_id):
        pass

    def _ref_link(self, user_id):
        link = self._bot.get_me().username
        result = 'https://t.me/' + link + '?start=' + str(user_id)

        return result

    @staticmethod
    def find_parents_ids(user_id):
        user_ids = []
        reg_user = User.objects(user_id=int(user_id)).first()
        while True:
            if reg_user.parent_referral_user_id:
                user_ids.append(reg_user.user_id)
                reg_user: User = User.objects(user_id=int(reg_user.parent_referral_user_id)).first()
            else:
                user_ids.append(reg_user.user_id)
                break
        return user_ids
