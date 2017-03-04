from telebot import types
import re
from datetime import date

class Utils:

    def gen_markup(self, list_item):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for item in list_item:
            markup.add(str(item))
        return markup

    def gen_markup_for_chat(self, list_item):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for item in list_item:
            markup.add(str(item))
        return markup

    def gen_inline_markup_for_list(self, login, data):
        markup = types.InlineKeyboardMarkup()
        inlineButton = types.InlineKeyboardButton(text='Войти в чат с %s' % login, callback_data='%s' % data)
        markup.add(inlineButton)
        return markup

    def gen_inline_markup_for_msg(self, login, data):
        markup = types.InlineKeyboardMarkup()
        login_inlineButton = types.InlineKeyboardButton(text='Войти в чат с %s' % login, callback_data='%s' % data)
        bl_inlineButton = types.InlineKeyboardButton(text='Добавить в черный список',
                                                     callback_data='back_list %s' % data)
        markup.add(login_inlineButton)
        markup.add(bl_inlineButton)
        return markup

    def gen_inline_markup_for_black_list(self, data):
        markup = types.InlineKeyboardMarkup()
        delete_from_bl_button = types.InlineKeyboardButton(text='Убрать из черного списка',
                                                           callback_data='delete_from_bl %s' % data)
        markup.add(delete_from_bl_button)
        return markup

    def gen_button(self, text):
        but = types.KeyboardButton(request_contact=True, request_location=True, text=text)
        mark = types.ReplyKeyboardMarkup()
        mark.add(but)
        return mark

    def markup_remove(self):
        markup_remove = types.ReplyKeyboardRemove()
        return markup_remove

    def dobtodate(self, dob):
        arr = re.split('[\\\.\-]', dob)
        a = arr[0]
        arr[0] = arr[2]
        arr[2] = a
        date = '-'.join(arr)
        return date

    def get_age(self, dob):
        today = date.today()
        age = today.year - dob.year
        if today.month < dob.month:
            age -= 1
        elif today.month == dob.month and today.day < dob.day:
            age -= 1
        return age