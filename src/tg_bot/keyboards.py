from telebot import types

from ..core.db_model.text.text import Text


def get_lang_keyboard(buttons_text):
    lang_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    for text in buttons_text:
        lang_kb.add(text)

    return lang_kb


def choose_lang_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=locale_text(lang, 'rus'),
                                         callback_data='language_state_inline_button_1_option')
    button2 = types.InlineKeyboardButton(text=locale_text(lang, 'eng'),
                                         callback_data='language_state_inline_button_2_option')
    keyboard.row(button1, button2)
    return keyboard


def main_menu_keyboard(lang):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = locale_text(lang, 'add_funds')
    button2 = locale_text(lang, 'pari')
    button3 = locale_text(lang, 'cash_refund')
    button4 = locale_text(lang, 'my_balance')
    button5 = locale_text(lang, 'addition')
    keyboard.row(button1, button2)
    keyboard.row(button3, button4)
    keyboard.row(button5)
    return keyboard


def additional_keyboard(lang, is_notification_active: bool):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=locale_text(lang, 'ask_question'),
                                         callback_data='main_menu_state_inline_button_1_option')
    button2 = types.InlineKeyboardButton(text=locale_text(lang, 'referals'),
                                         callback_data='main_menu_state_inline_button_2_option')
    button3 = types.InlineKeyboardButton(text=locale_text(lang, 'change_lang'),
                                         callback_data='main_menu_state_inline_button_3_option')
    button4 = types.InlineKeyboardButton(text=locale_text(lang, 'faq'),
                                         callback_data='main_menu_state_inline_button_4_option')
    keyboard.row(button1, button2)
    keyboard.row(button3, button4)

    text = locale_text(lang, 'notification_msg')
    if is_notification_active:
        text = text.format(
            locale_text(lang, 'active_notification_msg')
        )
        callback_text = 'main_menu_state_inline_button_8_option'
    else:
        text = text.format(
            locale_text(lang, 'unactive_notification_msg')
        )
        callback_text = 'main_menu_state_inline_button_7_option'

    button5 = types.InlineKeyboardButton(
        text=text,
        callback_data=callback_text
    )

    keyboard.row(button5)
    return keyboard


def additional_lang_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=locale_text(lang, 'rus'),
                                         callback_data='main_menu_state_inline_button_5_option')
    button2 = types.InlineKeyboardButton(text=locale_text(lang, 'eng'),
                                         callback_data='main_menu_state_inline_button_6_option')
    keyboard.row(button1, button2)
    return keyboard


def add_funds_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=locale_text(lang, 'bitcoin_msg'),
                                         callback_data='add_funds_state_inline_button_1_option')
    keyboard.row(button1)
    return keyboard


def apply_funds_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=locale_text(lang, 'apply_add_funds_button_msg'),
                                         callback_data='add_funds_state_inline_button_2_option')
    keyboard.row(button1)
    return keyboard


def up_down_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=locale_text(lang, 'down_button_msg'),
                                         callback_data='pari_state_inline_button_1_option')
    button2 = types.InlineKeyboardButton(text=locale_text(lang, 'up_button_msg'),
                                         callback_data='pari_state_inline_button_2_option')
    keyboard.row(button1, button2)
    return keyboard


def cash_refund_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=locale_text(lang, 'bitcoin_msg'),
                                         callback_data='cash_refund_state_inline_button_1_option')
    keyboard.row(button1)
    return keyboard


def locale_text(lang, tag):
    if not lang or not tag:
        return None

    text = Text.objects(tag=tag).first()

    if not text:
        return None

    return text.values.get(lang)
