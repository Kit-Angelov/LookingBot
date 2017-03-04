import config
import telebot
from utils import Utils
from postgresDB import PostgresDB

bot = telebot.TeleBot(config.token)

db = PostgresDB()
db.create_table_users()
db.close()
statDict = {}
info = {}
search_info = {}


# Вход

@bot.message_handler(commands=['start'])
def handler_start(message):
    markup_remove = Utils().markup_remove()
    bot.send_message(message.chat.id, config.start, reply_markup=markup_remove)
    chat_id = message.chat.id
    statDict[message.chat.id] = 'new'
    info[message.chat.id] = []
    db = PostgresDB()
    if not db.check_user(chat_id):
        db.close()
        info[message.chat.id].append(chat_id)
        bot.send_message(chat_id, config.regMsg)
        sex_list = ['мужчина', 'женщина']
        markup = Utils().gen_markup(sex_list)
        bot.send_message(message.chat.id, config.sexMsg, reply_markup=markup)
        statDict[message.chat.id] = 'sex'

    else:
        db.close()
        statDict[message.chat.id] = 'existUser'


# help

@bot.message_handler(commands=['help'])
def handler_help(message):
    markup_remove = Utils().markup_remove()
    statDict[message.chat.id] = 'help'
    bot.send_message(message.chat.id, 'Отправте сообщение администратору', reply_markup=markup_remove)


@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'help', content_types=['text'])
def handler_msg_help(message):
    markup_remove = Utils().markup_remove()
    bot.send_message(message.chat.id, 'Ваше сообщение отправлено администратору', reply_markup=markup_remove)
    text = message.chat.first_name + ': ' + message.text
    bot.send_message(config.admin_id, text)
    db = PostgresDB()
    if not db.check_user(message.chat.id):
        db.close()
        bot.send_message(message.chat.id, 'Вы не заполнили анкету')
        handler_start(message)
    else:
        db.close()
        statDict[message.chat.id] = 'existUser'


# Команда поиска

@bot.message_handler(commands=['search'])
def handler_search(message):
    chat_id = message.chat.id
    db = PostgresDB()
    if not db.check_user(chat_id):
        db.close()
        handler_start(message)
    else:
        db.close()
        sex_list = ['мужчину', 'женщину']
        markup = Utils().gen_markup(sex_list)
        bot.send_message(message.chat.id, config.searchMsg, reply_markup=markup)
        statDict[message.chat.id] = 'searchSex'
        search_info[message.chat.id] = []


# Команда черный список

@bot.message_handler(commands=['black_list'])
def handler_black_list(message):
    db = PostgresDB()
    if not db.check_user(message.chat.id):
        db.close()
        handler_start(message)
    else:
        statDict[message.chat.id] = 'existUser'
        black_str = db.get_black_list(message.chat.id)
        if black_str != '':
            black_list = black_str.split()
            for i in black_list:
                inline_markup = Utils().gen_inline_markup_for_black_list(i)
                login = db.get_user_login(int(i))
                bot.send_message(message.chat.id, login, reply_markup=inline_markup)
                db.close()
        else:
            bot.send_message(message.chat.id, 'Ваш черный список пуст')
            db.close()


# Отлов сообщений после перезапуска приложения

@bot.message_handler(func=lambda message: statDict.get(message.chat.id) is None, content_types=config.types)
def handler_text(message):
    chat_id = message.chat.id
    db = PostgresDB()
    if not db.check_user(chat_id):
        db.close()
        handler_start(message)
    else:
        markup_remove = Utils().markup_remove()
        statDict[message.chat.id] = 'existUser'
        bot.send_message(chat_id, 'Введите одну из команд', reply_markup=markup_remove)
        db.close()


# Регистрация

@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'sex', regexp='^мужчина$|^женщина$')
def handler_sex(message):
    markup_remove = Utils().markup_remove()
    sex = message.text[0]
    bot.send_message(message.chat.id, config.loginMsg, reply_markup=markup_remove)
    statDict[message.chat.id] = 'login'
    info[message.chat.id].append(sex)


@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'login', regexp='^[a-zA-Z0-9_]{2,64}$')
def handler_login(message):
    new_login = message.text
    bot.send_message(message.chat.id, config.picMsg)
    statDict[message.chat.id] = 'photo'
    info[message.chat.id].append(new_login)


@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'photo', content_types=['photo'])
def handeler_pic(message):
    pic_id = message.photo[0].file_id
    bot.send_message(message.chat.id, config.dobMsg)
    statDict[message.chat.id] = 'date'
    info[message.chat.id].append(pic_id)


@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'date', regexp=config.dateRegEx)
def handler_dob(message):
    dob = message.text
    dob = Utils().dobtodate(dob)
    bot.send_message(message.chat.id, config.descriptMsg)
    statDict[message.chat.id] = 'descript'
    info[message.chat.id].append(dob)


@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'descript', content_types=['text'])
def handler_descript(message):
    descript = message.text
    info[message.chat.id].append(descript)
    db = PostgresDB()
    db.add_user(info[message.chat.id][0], info[message.chat.id][2], info[message.chat.id][3],
                info[message.chat.id][4], info[message.chat.id][1], info[message.chat.id][5])
    bot.send_message(message.chat.id, config.endRegMsg)
    statDict[message.chat.id] = 'existUser'
    bot.send_photo(config.admin_id, info[message.chat.id][3])
    bot.send_message(config.admin_id, "Новый пользователь " + info[message.chat.id][2])


# поиск


@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'searchSex', regexp='^мужчину$|^женщину$')
def handler_search_sex(message):
    search_sex = message.text[0]
    age_list = ['16-20', '21-25', '26-30', '31-35', '36-40', '41-45', '46-50', '51-60']
    markup = Utils().gen_markup(age_list)
    bot.send_message(message.chat.id, config.searchAgeMsg, reply_markup=markup)
    statDict[message.chat.id] = 'searchAge'
    search_info[message.chat.id].append(search_sex)


@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'searchAge', regexp='^\d{2}\-\d{2}$')
def handler_search_age(message):
    search_age = message.text
    statDict[message.chat.id] = 'searchRes'
    search_info[message.chat.id].append(search_age)
    db = PostgresDB()
    markup_remove = Utils().markup_remove()
    res_search = db.search_user(search_info[message.chat.id][0], search_info[message.chat.id][1])
    db.close()
    for i in res_search:
        inline_markup = Utils().gen_inline_markup_for_list(i[1], i[0])
        age = Utils().get_age(i[3])
        text = 'Ник: ' + i[1] + '\nПол: ' + i[4] + '\nВозраст: ' + str(age) + '\nО себе: ' + i[5]
        bot.send_photo(message.chat.id, i[2], reply_markup=markup_remove)
        bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: True)
def handler_callback(call):
    if 'black_list' in call.data:
        black_user_id = int(call.data.split()[1])
        db = PostgresDB()
        db.in_black_list(black_user_id, call.message.chat.id)
        db.close()
        bot.send_message(call.message.chat.id, 'Пользователь добален в черный список')

    elif 'delete_from_bl' in call.data:
        delete_from_bl_id = int(call.data.split()[1])
        db = PostgresDB()
        db.delete_from_bl(delete_from_bl_id, call.message.chat.id)
        db.close()
        bot.send_message(call.message.chat.id, 'Пользователь удален из черного списка')

    else:
        markup = Utils().gen_markup_for_chat(['Выйти из чата'])
        chat_user_id = int(call.data)
        db = PostgresDB()
        login = db.get_user_login(chat_user_id)
        bot.send_message(call.message.chat.id, 'Вы в чате с %s' % login, reply_markup=markup)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=config.inChatMsg % (login, login))
        statDictInChat = 'in chat with ' + str(chat_user_id)
        statDict[call.message.chat.id] = statDictInChat


# Выход из чата


@bot.message_handler(func=lambda message: 'in chat with' in statDict.get(message.chat.id), regexp='^Выйти\sиз\sчата$')
def handler_out_from_chat(message):
    markup_remove = Utils().markup_remove()
    statDict[message.chat.id] = 'existUser'
    bot.send_message(message.chat.id, 'Вы вышли из чата', reply_markup=markup_remove)


# в чате


@bot.message_handler(func=lambda message: 'in chat with' in statDict.get(message.chat.id), content_types=config.types)
def send_in_chat(message):
    chat_user_id = statDict.get(message.chat.id)
    chat_user_id = int(chat_user_id.split(' ')[3])
    db = PostgresDB()
    get_with_user = db.get_user(chat_user_id)
    get_user = db.get_user(message.chat.id)
    db.close()
    if statDict.get(chat_user_id) == 'in chat with ' + str(get_user[0]) and str(get_user[0]) not in get_with_user[6]:
        text = 'От ' + get_user[1] + ': '
        if message.text:
            bot.send_message(chat_user_id, message.text)
            bot.send_message(config.admin_id, text + message.text)
        elif message.photo:
            bot.send_photo(chat_user_id, message.photo[0].file_id)
            bot.send_message(config.admin_id, text)
            bot.send_photo(config.admin_id, message.photo[0].file_id)
        elif message.audio:
            bot.send_audio(chat_user_id, message.audio.file_id)
        elif message.video:
            bot.send_video(chat_user_id, message.video.file_id)
        elif message.document:
            bot.send_document(chat_user_id, message.document.file_id)
        elif message.sticker:
            bot.send_sticker(chat_user_id, message.sticker.file_id)
        elif message.voice:
            bot.send_voice(chat_user_id, message.voice.file_id)
        elif message.location:
            bot.send_location(chat_user_id, message.location.latitude, message.location.longitude)
        elif message.contact:
            bot.send_contact(chat_user_id, message.contact.phone_number, message.contact.first_name)
            bot.send_message(config.admin_id, text)
            bot.send_contact(config.admin_id, message.contact.phone_number, message.contact.first_name)
        else:
            bot.send_message(chat_user_id, 'отправлен недопустимый файл')

    elif str(get_user[0]) not in get_with_user[6]:
        inline_markup = Utils().gen_inline_markup_for_msg(get_user[1], get_user[0])
        text = 'От ' + get_user[1] + ': '
        if message.text:
            bot.send_message(chat_user_id, text + message.text, reply_markup=inline_markup)
        elif message.photo:
            bot.send_message(chat_user_id, text)
            bot.send_photo(chat_user_id, message.photo[0].file_id, reply_markup=inline_markup)
        elif message.audio:
            bot.send_message(chat_user_id, text)
            bot.send_audio(chat_user_id, message.audio.file_id, reply_markup=inline_markup)
        elif message.video:
            bot.send_message(chat_user_id, text)
            bot.send_video(chat_user_id, message.video.file_id, reply_markup=inline_markup)
        elif message.document:
            bot.send_message(chat_user_id, text)
            bot.send_document(chat_user_id, message.document.file_id, reply_markup=inline_markup)
        elif message.sticker:
            bot.send_message(chat_user_id, text)
            bot.send_sticker(chat_user_id, message.sticker.file_id, reply_markup=inline_markup)
        elif message.voice:
            bot.send_message(chat_user_id, text)
            bot.send_voice(chat_user_id, message.voice.file_id, reply_markup=inline_markup)
        elif message.location:
            bot.send_message(chat_user_id, text)
            bot.send_location(chat_user_id, message.location.latitude, message.location.longitude,
                                                                                    reply_markup=inline_markup)
        elif message.contact:
            bot.send_message(chat_user_id, text)
            bot.send_contact(chat_user_id, message.contact.phone_number, message.contact.first_name,
                                                                                    reply_markup=inline_markup)
        else:
            bot.send_message(chat_user_id, text)
            bot.send_message(chat_user_id, 'отправлен недопустимый файл')

    else:
        bot.send_message(message.chat.id, 'Вы в черном списке у ' + get_with_user[1])


# отлов свободных сообщений


@bot.message_handler(func=lambda message: statDict.get(message.chat.id) == 'existUser', content_types=config.types)
def handler_text(message):
    chat_id = message.chat.id
    db = PostgresDB()
    if not db.check_user(chat_id):
        db.close()
        handler_start(message)
    else:
        bot.send_message(chat_id, 'Введите одну из команд')
        db.close()


if __name__ == '__main__':
    bot.polling(none_stop=True)


