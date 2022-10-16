import requests
import telebot
import json
from telebot import types
# Создаем экземпляр бота
# Название бота в телеграмме: @botTourismAssistant
bot = telebot.TeleBot('5688811341:AAF3VuE8ZDtdH_jipdlY8c8f0jpNgKvZG2Y')
url = 'https://catalog.api.2gis.com/3.0/items'
coord = None

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Вас приветствует TourismAssistant )')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item5 = types.KeyboardButton(text="coord", request_location=True)
    markup.add(item5)
    bot.send_message(m.chat.id, 'Разрешите отправку своих координат', reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_loc(m):
    global coord
    coord = m.location
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Поиск мест")
    item2 = types.KeyboardButton("Поиск билетов")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(m.chat.id, 'Выберите, что хотите посмотреть', reply_markup=markup)
    print(m.location)

    
# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'Поиск мест' :
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item3 = types.KeyboardButton("Кафе")
        item4 = types.KeyboardButton("Достопримечательности")
        markup.add(item3)
        markup.add(item4)
        bot.send_message(message.chat.id, 'Выберите категорию мест',reply_markup=markup)
    elif message.text.strip() == 'Поиск билетов':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item5 = types.KeyboardButton("Концерт")
        item6 = types.KeyboardButton("Театр")
        markup.add(item5)
        markup.add(item6)
        bot.send_message(message.chat.id, 'Выберите категорию билетов',reply_markup=markup)
    elif message.text.strip() == 'Кафе':
        # Потом переедет в отдельный файл
        params = dict(q='кафе', sort_point=str(coord.longitude)+','+str(coord.latitude), key='ruimey3930')
        str1 = str('https://catalog.api.2gis.com/3.0/items?q=кафе&sort_point='+str(coord.longitude)+','+str(coord.latitude)+'&key=ruimey3930')
        req = requests.get(str1)
        print(req.text)
        listResult = parseResponse(req.text, message.chat.id)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Поиск мест")
        item2 = types.KeyboardButton("Поиск билетов")
        markup.add(item1)
        markup.add(item2)
        bot.send_message(message.chat.id, 'Выберите, что хотите посмотреть', reply_markup=markup)


def parseResponse(text, id):
    dic = json.loads(text)
    items = []
    o = dic.get('result')
    for i in o.get('items'):
        l = dict(i)
        u=tuple()
        strName = l['name']
        strLink=None
        try:
            strLink = l['ads']['link']['value']
        except:
            strLink = "There is no link"
        u = {strName, strLink}
        items.append(u)
        bot.send_message(id, strName+': ' + strLink)
    return items

# Запускаем бота
bot.polling(none_stop=True, interval=0)