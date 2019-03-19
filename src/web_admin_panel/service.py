import hashlib
import random
import time
import datetime
import telebot
from math import ceil

from flask import Flask, render_template, request, make_response, redirect, send_from_directory
from flask_bootstrap import Bootstrap
from flask_mongoengine import MongoEngine

from .. import config

from .db_model.user import User

from ..tg_bot.db_model.user import User as TgUser


from ..core.db_model.core import Core
from ..core.db_model.core_history import CoreHistory

from ..core.db_model.text.text import Text
from ..core.db_model.questions import Question
from ..core.db_model.text.language import Language
from ..core.db_model.message import Message, EditMessage, EditMessageEng
from ..core.db_model.refund import Refund
from ..core.db_model.pari_bet import PariBet

from telebot import TeleBot
from ..config import BOT_TOKEN

bot = TeleBot(BOT_TOKEN)

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = config.PROJECT_NAME

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['MONGODB_SETTINGS'] = {
    'db': config.PROJECT_NAME,
    'alias':  'default'
}

Bootstrap(app=app)
MongoEngine(app=app)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = make_response(redirect('login'))
    if auth_check():
        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()

        if not user:
            return None

        core: Core = Core.objects.first()
        if not core:
            core = Core()
            core.save()

        if request.method == 'POST':
            api_key = request.form.get('value')
            if api_key:
                core.api_key = api_key
                core.save()
            else:
                error = 'Вы не ввели API key'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            bet_chanel = request.form.get('profit_bot_chanel')
            if bet_chanel:
                core.channel_link = bet_chanel
                core.save()
            else:
                error = 'Вы не ввели chanel'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            secret_key = request.form.get('value1')
            if secret_key:
                core.secret_key = secret_key
                core.save()
            else:
                error = 'Вы не ввели Secure key'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            main_btc_address = request.form.get('main_btc_address')
            if main_btc_address:
                core.main_btc_address = main_btc_address
                core.save()
            else:
                error = 'Вы не ввели поле Binance Address Btc для ввода'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            referral_bonus_price = request.form.get('referral_bonus_price')
            if referral_bonus_price:
                core.referral_bonus_price = float(referral_bonus_price)
                core.save()
            else:
                error = 'Вы не ввели поле Реферальный Бонус'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            referral_bonus_2_price = request.form.get('referral_bonus_2_price')
            if referral_bonus_2_price:
                core.referral_bonus_2_price = float(referral_bonus_2_price)
                core.save()
            else:
                error = 'Вы не ввели поле Реферальный Бонус'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            profit_bot_percent = request.form.get('profit_bot_percent')
            if profit_bot_percent:
                core.profit_percent = 100.0 - float(profit_bot_percent)
                core.save()
            else:
                error = 'Вы не ввели поле % Профита Бота'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            fee_username = request.form.get('fee_username')
            if fee_username:
                core.fee_username = fee_username
                core.save()
            else:
                error = 'Вы не ввели поле Юзер который забирает % Профита Бота'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            link_1 = request.form.get('link_1')
            if link_1:
                core.link_1 = link_1
                core.save()
            else:
                error = 'Вы не ввели поле Rus Link'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            link_2 = request.form.get('link_2')
            if link_2:
                core.link_2 = link_2
                core.save()
            else:
                error = 'Вы не ввели поле Eng Link'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            min_bet_size = request.form.get('min_bet_size')
            if min_bet_size:
                core.min_bet_size = float(min_bet_size)
                core.save()
            else:
                error = 'Вы не ввели поле Мин. ставка в боте (BTC)'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            intermedia_period_1_info = request.form.get('intermedia_period_1_info')
            if intermedia_period_1_info:
                core.intermedia_period_1_info = int(intermedia_period_1_info)
                core.save()
            else:
                error = 'Вы не ввели поле Интервал между пари (мин)'
                result = make_response(render_template('index.html', error=error, core=core))
                return result

            intermedia_period_2_info = request.form.get('intermedia_period_2_info')
            if intermedia_period_2_info:
                core.intermedia_period_2_info = int(intermedia_period_2_info)
                core.save()
            else:
                error = 'Вы не ввели поле Интервал после начала пари для закрытия (мин)'
                result = make_response(render_template('index.html', error=error, core=core))
                return result
        ref_bonus_1 = core.referral_bonus_price
        ref_bonus_2 = core.referral_bonus_2_price
        ref_bonus_1 = from_dublicate_to_str(ref_bonus_1)
        ref_bonus_2 = from_dublicate_to_str(ref_bonus_2)
        result = render_template(template_name_or_list='index.html', ref_bonus_1=ref_bonus_1,
                                 ref_bonus_2=ref_bonus_2,
                                 core=core)
    return result


@app.route('/bets/edit/', methods=['GET', 'POST'])
def edit_bet():
    core = Core.objects().first()
    indent = _is_current_pari(core.current_open_pari_time)
    if indent:
        result = make_response(redirect('bets'))
        core = Core.objects().first()
        pari_bet = PariBet.objects(tag=core.current_open_pari_bet_tag)
        core = Core.objects.first()
        plus_people_counter = 0
        plus_bets_counter = 0
        minus_people_counter = 0
        minus_bets_counter = 0
        if pari_bet:
            for bet in pari_bet:
                if bet.is_up:
                    plus_people_counter += 1
                    plus_bets_counter += bet.balance
                else:
                    minus_people_counter += 1
                    minus_bets_counter += bet.balance


        if request.method == 'POST':

            up_num_member = request.form.get('up_num_member')
            if up_num_member:
                core.current_open_pari_virtual_members_up = float(up_num_member)
            else:
                error = 'Вы не ввели баланс!'
                result = make_response(render_template('bet.html', error=error, core=core))
                return result

            down_num_member = request.form.get('down_num_member')
            if down_num_member:
                core.current_open_pari_virtual_members_down = float(down_num_member)
            else:
                error = 'Вы не ввели баланс!'
                result = make_response(render_template('bet.html', error=error, core=core))
                return result

            up_balance = request.form.get('up_balance')
            if up_balance:
                core.current_open_pari_virtual_up_sum_balance = float(up_balance)
            else:
                error = 'Вы не ввели баланс!'
                result = make_response(render_template('bet.html', error=error, core=core))
                return result

            down_balance = request.form.get('down_balance')
            if down_balance:
                core.current_open_pari_virtual_down_sum_balance = float(down_balance)
            else:
                error = 'Вы не ввели баланс!'
                result = make_response(render_template('bet.html', error=error, core=core))
                return result

            core.save()
        else:
            core = Core.objects.first()
            result = make_response(render_template('bet.html', core=core, pari_bet=pari_bet,
                                                   plus_people_counter=plus_people_counter, plus_bets_counter=plus_bets_counter, minus_people_counter=minus_people_counter, minus_bets_counter=minus_bets_counter))
            return result

        return result
    else:
        result = make_response(redirect('bets'))
        return result


@app.route('/bets/view/<string:pari_id>', methods=['GET', 'POST'])
def view_bet(pari_id):
    result = make_response(redirect('login'))
    if auth_check():
        if not pari_id:
            return make_response(redirect('bets'))
        else:
            pari: CoreHistory = CoreHistory.objects(id=pari_id).first()
            bets: PariBet = PariBet.objects(tag=pari.pari_bet_tag)
            result1 = [{bet.user_id: {'balance': bet.balance,
                                    'is_up': bet.is_up}} for bet in bets]

            result2 = list()
            for bet in bets:
                if bet.victory_result:
                    percent = bet.victory_result / pari.open_pari_balance * 100
                    data = {bet.user_id: percent}
                    result2.append(data)
            return make_response(render_template(template_name_or_list='bet_view.html', row1=result1, result2=result2))

    else:
        return result


@app.route('/user/edit/<string:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    result = make_response(redirect('users'))

    if not user_id:
        return result

    target_user = TgUser.objects(id=user_id).first()

    if request.method == 'POST':
        balance = request.form.get('balance')
        if balance:
            target_user.balance = float(balance)
        else:
            error = 'Вы не ввели баланс!'
            result = make_response(render_template('user.html', error=error, user=target_user))
            return result

        target_user.save()
        result = make_response(redirect('users'))
    else:
        if target_user:
            result = render_template(template_name_or_list='user.html',
                                     user=target_user)

    return result


@app.route('/bets', methods=['GET', 'POST'])
def bets():
    result = make_response(redirect('login'))
    if auth_check():
        page = int(request.args.get('p', None)) if request.args.get('p', None) else 1

        session_id = request.cookies.get('session_id', None)
        core = Core.objects.first()
        core_history: CoreHistory = CoreHistory



        if not core:
            return None

        if request.method == 'POST':
            pass
        else:
            end = page * 20
            start = end - 20
            bets_len = Core.objects.count()+CoreHistory.objects.count()

            p_all = ceil(bets_len / 20) if ceil(bets_len / 20) != 0 else 1

            if start > bets_len:
                start = bets_len

            if end > bets_len:
                end = bets_len

            tg_core = Core.objects[start:end]
            indent = _is_current_pari(core.current_open_pari_time)
            tg_core_history: CoreHistory = CoreHistory.objects[start:end].order_by('-pari_bet_tag')
            balance = core.current_open_pari_sum_up_balance+core.current_open_pari_sum_down_balance
            result = render_template(template_name_or_list='bets.html', p=page,
                                     rows=tg_core, p_all=p_all, balance=balance,
                                     u_all=bets_len, historys=tg_core_history, indent=indent)
            print(tg_core)
    return result


@app.route('/bets/del/<string:pari_bet_tag>', methods=['GET', 'POST'])
def del_bets(pari_bet_tag):
    print(pari_bet_tag)
    result = make_response(redirect('bets'))

    if not pari_bet_tag:
        return result

    target_history: CoreHistory = CoreHistory.objects(id=pari_bet_tag).first()
    target_history.delete()

    return result


@app.route('/earn_orders', methods=['GET', 'POST'])
def earn_orders():
    result = make_response(redirect('login'))
    if auth_check():
        page = int(request.args.get('p', None)) if request.args.get('p', None) else 1
        core = Core.objects.first()

        if not core:
            return None

        if request.method == 'POST':
            pass
        else:
            result = render_template(
                template_name_or_list='earn_orders.html',
                rows_1=core.txid_for_check,
                rows_2=core.used_txid,
            )

    return result


@app.route('/users', methods=['GET', 'POST'])
def users():
    result = make_response(redirect('login'))
    if auth_check():
        page = int(request.args.get('p', None)) if request.args.get('p', None) else 1

        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()

        if not user:
            return None

        if request.method == 'POST':
            pass
        else:
            end = page * 20
            start = end - 20
            users_len = TgUser.objects.count()

            p_all = ceil(users_len / 20) if ceil(users_len / 20) != 0 else 1

            if start > users_len:
                start = users_len

            if end > users_len:
                end = users_len

            tg_users = TgUser.objects[start:end]
            result = render_template(template_name_or_list='users.html', p=page, rows=tg_users, p_all=p_all,
                                     u_all=users_len)
    return result





@app.route('/user/block/<string:user_id>', methods=['GET', 'POST'])
def block_user(user_id):


    result = make_response(redirect('users'))

    if not user_id:
        return result

    target_user = TgUser.objects(id=user_id).first()

    if target_user:
        target_user.is_blocked = not target_user.is_blocked
        target_user.save()
        if target_user.is_blocked:
            text = locale_text(target_user.user_lang, 'block_msg')
            bot.send_message(target_user.user_id, text)
        else:
            text = locale_text(target_user.user_lang, 'unblock_msg')
            bot.send_message(target_user.user_id, text)


    return result


@app.route('/user/find', methods=['POST'])
def find_user():
    result = make_response(redirect('/users'))

    user_id = request.form.get('user_id')
    try:
        target_user: TgUser = TgUser.objects(user_id=int(user_id)).first()

        if user_id:
            result = make_response(redirect('/user/edit/'+str(target_user.id)))
    except:
        pass

    return result


@app.route('/user/del/<string:user_id>', methods=['GET', 'POST'])
def del_user(user_id):
    result = make_response(redirect('users'))

    if not user_id:
        return result

    target_user: TgUser = TgUser.objects(id=user_id).first()
    target_user.delete()

    return result


# language adding and editing
@app.route('/languages', methods=['GET', 'POST'])
def languages_method():
    result = make_response(redirect('login'))
    if auth_check():
        page = int(request.args.get('p', None)) if request.args.get('p', None) else 1

        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()

        if not user:
            return None

        if request.method == 'POST':
            pass
        else:
            end = page * 20
            start = end - 20
            languages_len = Language.objects.count()

            p_all = ceil(languages_len / 20) if ceil(languages_len / 20) != 0 else 1

            if start > languages_len:
                start = languages_len

            if end > languages_len:
                end = languages_len

            languages = Language.objects[start:end]
            result = render_template(template_name_or_list='languages.html', p=page, rows=languages, p_all=p_all,
                                     u_all=languages_len)
    return result


@app.route('/language', methods=['GET', 'POST'])
def language_method():
    result = make_response(redirect('login'))
    if auth_check():
        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()

        if not user:
            return None

        if request.method == 'POST':
            new_language = Language()

            name = request.form['name']
            if name:
                new_language.name = name
            else:
                error = 'Вы не ввели название!'
                result = make_response(render_template('language.html', error=error))
                return result

            tag = request.form['tag']
            if tag:
                new_language.tag = tag
            else:
                error = 'Вы не ввели тег!'
                result = make_response(render_template('language.html', error=error))
                return result

            button_text = request.form['button_text']
            if tag:
                new_language.button_text = button_text
            else:
                error = 'Вы не ввели текст кнопки!'
                result = make_response(render_template('language.html', error=error))
                return result

            new_language.save()
            result = make_response(redirect('languages'))
        else:
            result = render_template(template_name_or_list='language.html')

    return result


@app.route('/language/edit/<string:language_id>', methods=['GET', 'POST'])
def edit_language(language_id):
    result = make_response(redirect('languages'))

    if not language_id:
        return result

    target_language = Language.objects(id=language_id).first()

    if request.method == 'POST':
        name = request.form['name']
        if name:
            target_language.name = name
        else:
            error = 'Вы не ввели название!'
            result = make_response(render_template('language.html', error=error))
            return result

        tag = request.form['tag']
        if tag:
            target_language.tag = tag
        else:
            error = 'Вы не ввели тег!'
            result = make_response(render_template('language.html', error=error))
            return result

        button_text = request.form['button_text']
        if tag:
            target_language.button_text = button_text
        else:
            error = 'Вы не ввели текст кнопки!'
            result = make_response(render_template('language.html', error=error))
            return result

        target_language.save()
        result = make_response(redirect('languages'))
    else:
        if target_language:
            result = render_template(template_name_or_list='language.html',
                                     target_language=target_language)

    return result


@app.route('/language/del/<string:language_id>')
def del_language(language_id):
    result = make_response(redirect('languages'))

    if not language_id:
        return result

    target_language = Language.objects(id=language_id).first()

    if target_language:
        target_language.delete()

    return result


# text adding and editing
@app.route('/texts', methods=['GET', 'POST'])
def texts_method():
    result = make_response(redirect('login'))
    if auth_check():
        page = int(request.args.get('p', None)) if request.args.get('p', None) else 1

        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()

        if not user:
            return None

        if request.method == 'POST':
            pass
        else:
            end = page * 20
            start = end - 20
            texts_len = Text.objects.count()

            p_all = ceil(texts_len / 20) if ceil(texts_len / 20) != 0 else 1

            if start > texts_len:
                start = texts_len

            if end > texts_len:
                end = texts_len

            texts = Text.objects[start:end]
            result = render_template(template_name_or_list='texts.html', p=page, rows=texts, p_all=p_all,
                                     u_all=texts_len)

    return result


@app.route('/text', methods=['GET', 'POST'])
def text_method():
    result = make_response(redirect('login'))
    if auth_check():
        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()
        languages = Language.objects

        if not user:
            return None

        if request.method == 'POST':
            new_text = Text()

            tag = request.form.get('tag')
            if tag:
                new_text.tag = tag
            else:
                error = 'Вы не ввели тег!'
                result = make_response(render_template('text.html', languages=languages, error=error))
                return result

            for language in languages:
                value = request.form.get(language.tag + '_value')
                if value:
                    new_text.values[language.tag] = value
                else:
                    error = 'Вы не ввели значение  для языка: ' + language.name + '!'
                    result = make_response(render_template('text.html', languages=languages, error=error))
                    return result
            new_text.save()
            result = make_response(redirect('texts'))
        else:
            result = render_template(template_name_or_list='text.html', languages=languages)

    return result


@app.route('/text/edit/<string:text_id>', methods=['GET', 'POST'])
def edit_text(text_id):
    result = make_response(redirect('languages'))

    if not text_id:
        return result

    languages = Language.objects

    target_text = Text.objects(id=text_id).first()

    if not target_text:
        return None

    if request.method == 'POST':
        tag = request.form.get('tag')
        if tag:
            target_text.tag = tag
        else:
            error = 'Вы не ввели тег!'
            result = make_response(render_template('text.html', target_text=target_text, languages=languages,
                                                   error=error))
            return result

        for language in languages:
            value = request.form.get(language.tag + '_value')
            if value:
                target_text.values[language.tag] = value
            else:
                error = 'Вы не ввели значение  для языка: ' + language.name + '!'
                result = make_response(render_template('text.html', target_text=target_text, languages=languages,
                                                       error=error))
                return result
        target_text.save()
        result = make_response(redirect('texts'))
    else:
        result = render_template(template_name_or_list='text.html',
                                 target_text=target_text,
                                 languages=languages)

    return result


@app.route('/text/del/<string:text_id>', methods=['GET', 'POST'])
def del_text(text_id):
    result = make_response(redirect('/'))

    if not text_id:
        return result

    target_text = Text.objects(id=text_id).first()

    if target_text:
        target_text.delete()
        result = make_response(redirect('texts'))

    return result


@app.route('/mailing', methods=['GET', 'POST'])
def mailing():
    result = make_response(redirect('login'))

    if auth_check():
        error = None
        if request.method == 'POST':
            core = Core.objects.first()

            if core:
                message = Message()
                data = datetime.datetime.now()
                message.data = str(data)
                message.language = request.form.get('language')
                message.text = request.form.get('message')
                message.save()

                core.update(push__messages=message)
                core.reload()

        edit_rus: EditMessage = EditMessage.objects()
        edit_eng: EditMessageEng = EditMessageEng.objects()
        tg_users = TgUser.objects
        result = render_template(template_name_or_list='mailing.html', edit_rus=edit_rus,
                                 edit_eng=edit_eng,
                                 users=tg_users,
                                 error=error)

    return result


@app.route('/mailing/edit/<string:message_id>/<string:lang>', methods=['GET', 'POST'])
def edit_mailing(message_id, lang):
    result = make_response(redirect('login'))
    if auth_check():
        error = None
        if lang == 'rus':
            edit: EditMessage = EditMessage.objects(id=message_id).first()
        elif lang == 'eng':
            edit: EditMessageEng = EditMessageEng.objects(id=message_id).first()

        if request.method == 'POST':
            text = request.form.get('edit_message')
            if text:
                for i in edit.edit_mailing:
                    print(type(i))
                    bot.edit_message_text(text, i, edit.edit_mailing[i])
                edit.text = text
                edit.save()
            return redirect('/mailing')

        result = render_template(template_name_or_list='edit_mailing.html',
                                 error=error, edit=edit)

    return result


@app.route('/login', methods=['GET', 'POST'])
def login():
    result = make_response(render_template('login.html'))

    if not User.objects().first():
        user: User = User()
        user.login = 'paribot'
        user.password = hashlib.md5('qwerty12345'.encode('utf-8')).hexdigest()
        user.save()

    if request.method == 'POST':
        user_login = request.form['login']
        password = request.form['password']

        user = User.objects(login=user_login).first()

        if user and user.password == hashlib.md5(password.encode('utf-8')).hexdigest():
            hash_str = (user_login + password + str(random.randrange(111, 999))).encode('utf-8')
            hashed_pass = hashlib.md5(hash_str).hexdigest()
            session_id = hashed_pass
            time_alive = time.time() + (86400 * 7)

            user.session_id = session_id
            user.time_alive = time_alive
            user.save()

            result = make_response(redirect(''))
            result.set_cookie('session_id', session_id)
        else:
            error = 'Пользователь с таким логином/паролем не найден!'
            result = make_response(render_template('login.html', error=error))
    else:
        if auth_check():
            result = make_response(redirect(''))

    return result


# text adding and editing
@app.route('/questions', methods=['GET', 'POST'])
def questions_method():
    result = make_response(redirect('login'))
    if auth_check():
        page = int(request.args.get('p', None)) if request.args.get('p', None) else 1

        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()

        if not user:
            return None

        if request.method == 'POST':
            pass
        else:
            end = page * 20
            start = end - 20
            questions_len = Question.objects.count()

            p_all = ceil(questions_len / 20) if ceil(questions_len / 20) != 0 else 1

            if start > questions_len:
                start = questions_len

            if end > questions_len:
                end = questions_len

            questions = Question.objects[start:end]
            result = render_template(template_name_or_list='questions.html', p=page, rows=questions, p_all=p_all,
                                     u_all=questions_len)

    return result


@app.route('/question/send/<string:question_id>', methods=['GET', 'POST'])
def question_method(question_id):
    result = make_response(redirect('questions'))
    if auth_check():
        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()
        languages = Language.objects

        if not user:
            return None
        target_question: Question = Question.objects(id=question_id).first()

        if request.method == 'POST':
            answer = request.form['answer']
            if answer:
                text = '*Ваш вопрос: *{0}\n\n'.format(target_question.text)
                text = text + '*Ответ: *{0}'.format(answer)
                bot.send_message(target_question.user_id, text, parse_mode='markdown')
               # target_question.delete()
                target_question.status = 'Отвечено'
                target_question.save()

            else:
                error = 'Вы не ввели ответ'
                result = make_response(render_template('question.html', error=error))
                return result
        else:
            result = render_template(template_name_or_list='question.html')

    return result


@app.route('/question/del/<string:question_id>', methods=['GET', 'POST'])
def del_question(question_id):
    result = make_response(redirect('/'))

    if not question_id:
        return result

    target_question = Question.objects(id=question_id).first()

    if target_question:
        target_question.delete()
        result = make_response(redirect('questions'))

    return result


@app.route('/refunds', methods=['GET', 'POST'])
def refunds_method():
    result = make_response(redirect('login'))
    if auth_check():
        page = int(request.args.get('p', None)) if request.args.get('p', None) else 1

        session_id = request.cookies.get('session_id', None)
        user = User.objects(session_id=session_id).first()

        if not user:
            return None

        if request.method == 'POST':
            pass
        else:
            end = page * 20
            start = end - 20
            refund_len = Refund.objects.count()

            p_all = ceil(refund_len / 20) if ceil(refund_len / 20) != 0 else 1

            if start > refund_len:
                start = refund_len

            if end > refund_len:
                end = refund_len

            refunds = Refund.objects[start:end]
            result = render_template(template_name_or_list='refunds.html', p=page, rows=refunds, p_all=p_all,
                                     u_all=refund_len)

    return result


@app.route('/refund/del/<string:refund_id>', methods=['GET', 'POST'])
def del_refund(refund_id):
    result = make_response(redirect('/'))

    if not refund_id:
        return result

    target_refund = Refund.objects(id=refund_id).first()

    if target_refund:
        target_refund.delete()
        result = make_response(redirect('refunds'))

    return result


@app.route('/refund/pay/<string:refund_id>', methods=['GET', 'POST'])
def pay_refund(refund_id):
    result = make_response(redirect('refunds'))

    if not refund_id:
        return result

    target_refund = Refund.objects(id=refund_id).first()
    target_user = TgUser.objects(user_id=target_refund.user_id).first()
    target_user.balance = target_user.balance - target_refund.sum
    target_refund.paid_off = 'Выплачено'
    target_refund.save()
    target_user.save()

    if target_refund:
        result = make_response(redirect('refunds'))

    return result


@app.route('/logout')
def logout():
    result = make_response(redirect('login'))

    session_id = request.cookies.get('session_id', None)
    if session_id:
        result.set_cookie('session_id', 'deleted', expires=time.time()-100)

    return result


def locale_text(lang, tag):
    if not lang or not tag:
        return None

    text = Text.objects(tag=tag).first()

    if not text:
        return None

    return text.values.get(lang)


def auth_check():
    result = False

    session_id = request.cookies.get('session_id', None)
    if session_id:
        user = User.objects(session_id=session_id).first()
        if user:
            result = True

    return result

def from_dublicate_to_str(data):
    precision = 5
    data = f'{data:.{precision}f}'
    return data

def _is_current_pari(start_time):
    delta = datetime.timedelta(minutes=10)
    if datetime.datetime.utcnow()-start_time < delta:
        return True
    else:
        return False

