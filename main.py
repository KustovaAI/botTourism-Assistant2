import math

import requests
import telebot
import json
from telebot import types
# Создаем экземпляр бота
# Название бота в телеграмме: @botTourismAssistant
bot = telebot.TeleBot('5688811341:AAF3VuE8ZDtdH_jipdlY8c8f0jpNgKvZG2Y')
url = 'https://catalog.api.2gis.com/3.0/items'
u = dict()
userDict = dict()

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Вас приветствует TourismAssistant )')
    userDict[m.chat.id] = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item5 = types.KeyboardButton(text="Отправить свои координаты", request_location=True)
    markup.add(item5)
    bot.send_message(m.chat.id, 'Разрешите отправку своих координат', reply_markup=markup)

# Здесь ожидаем и получаем координаты пользователя
@bot.message_handler(content_types=['location'])
def handle_loc(m):
    userDict[m.chat.id] = {'coords' : m.location}
    global coord
    coord = m.location
    # Здесь можно собрать логи
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item3 = types.KeyboardButton("Кафе")
    item4 = types.KeyboardButton("Достопримечательности")
    item5 = types.KeyboardButton("Статистика")
    markup.add(item3)
    markup.add(item4)
    markup.add(item5)
    bot.send_message(m.chat.id, 'Выберите, что хотите посмотреть', reply_markup=markup)
    print(m.location)

    
# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'Кафе':
        # Отправляем запрос в 2gis по кафе и ждем ответа
        user = userDict[message.chat.id]
        str1 = str('https://catalog.api.2gis.com/3.0/items?q=кафе&sort_point='+str(user['coords'].longitude)+','+str(user['coords'].latitude)+'&key=ruimey3930')
        req = requests.get(str1)
        print(req.text)
        listResult = parseResponseCaffee(req.text) # Выбираем имя, адрес, ссылку и описание из ответа. Заносим в список
        user = userDict[message.chat.id]
        user['listResultCaffee'] = listResult  # Здесь можно добавить в логирование, каи=кие кафешки ему чаще всего возвращали
        userDict[message.chat.id] = user
        sendButtonsCaffee(message.chat.id, listResult)  # Вывод информации о кафешках в удобном виде
    elif message.text.strip() == 'Достопримечательности':
        # Отправляем запрос в 2gis по достопримечательностям и ждем ответа
        user = userDict[message.chat.id]
        str1 = str('https://catalog.api.2gis.com/3.0/items?q=достопримечательности&sort_point='+str(user['coords'].longitude)+','+str(user['coords'].latitude)+'&key=ruimey3930')
        req = requests.get(str1)
        print(req.text)
        listResult = parseResponsePlaces(req.text) # Выбираем имя, адрес из ответа. Заносим в список
        user = userDict[message.chat.id]
        user['listResultPlace'] = listResult    # Здесь можно добавить в логирование, какие места ему чаще всего возвращали
        userDict[message.chat.id] = user
        sendButtonsPlaces(message.chat.id, listResult)
    elif "Caffee" in message.text.strip():
        # Если пользователь нажал на кнопку по какому-нибудь кафе, выводим всю инфу
        # Здесь можно добавить логирование, какие кафешки он чаще всего просматривал
        s=message.text.strip()
        placeName=s[s.find(" ") + 1:]   # Берём название кафе из кнопки
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Заказать такси")
        item2 = types.KeyboardButton("В начало")
        markup.add(item1)
        markup.add(item2)
        user = userDict[message.chat.id]
        user['lastSelectedPlaceName'] = placeName
        user['lastSelectedPlaceAddress'] = user['listResultCaffee'][placeName][1]
        userDict[message.chat.id] = user
        bot.send_message(message.chat.id, placeName+"\n Ссылка: " + user['listResultCaffee'][placeName][0] + "\n Адрес: "
                         + user['listResultCaffee'][placeName][1] + "\n Описание: " + user['listResultCaffee'][placeName][2], reply_markup=markup)
    elif "Place" in message.text.strip():
        # Если пользователь нажал на кнопку по какому-нибудь достопримеч., выводим всю инфу
        # Здесь можно добавить логирование, какие места он чаще всего просматривал
        s=message.text.strip()
        placeName=s[s.find(" ") + 1:]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Заказать такси")
        item2 = types.KeyboardButton("В начало")
        markup.add(item1)
        markup.add(item2)
        user = userDict[message.chat.id]
        user['lastSelectedPlaceName'] = placeName
        user['lastSelectedPlaceAddress'] = user['listResultPlace'][placeName][0]
        userDict[message.chat.id] = user
        bot.send_message(message.chat.id, placeName+"\n  Адрес: " + user['listResultPlace'][placeName][0] , reply_markup=markup)
    elif message.text.strip() == 'В начало':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Кафе")
        item2 = types.KeyboardButton("Достопримечательности")
        item3 = types.KeyboardButton("Статистика")
        markup.add(item1)
        markup.add(item2)
        markup.add(item3)
        bot.send_message(message.chat.id, 'Выберите, что хотите посмотреть', reply_markup=markup)
    elif message.text.strip() == "Заказать такси":
        user = userDict[message.chat.id]
        placeAddress = user['lastSelectedPlaceAddress']
        # Здесь по адресу обращаемся к другому api 2gis что бы по адресу получить координаты
        # Можно добавить в логирование адрес
        req = requests.get('https://catalog.api.2gis.com/3.0/items/geocode?q='+ placeAddress +'&fields=items.point&key=ruimey3930')
        listCoords = parseResponseCoordsByAddress(req.text, user['coords'].latitude, user['coords'].longitude)
        # Здесь по полученным координатам формируем ссылку на такси
        linkToTaxi=str('https://3.redirect.appmetrica.yandex.com/route?start-lat='+ str(user['coords'].latitude) + '&start-lon=' + str(user['coords'].longitude)
                           + '&end-lat=' + str(listCoords[0]) + '&end-lon=' + str(listCoords[1]) + '&appmetrica_tracking_id=25395763362139037')
        print(req.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("В начало")
        markup.add(item1)
        bot.send_message(message.chat.id, linkToTaxi, reply_markup=markup)


def parseResponseCaffee(text):
    dic = json.loads(text)
    o = dic.get('result')
    for i in o.get('items'):
        l = dict(i)
        strName = l['name']
        strLink=None
        try:
            strLink = l['ads']['link']['value']
        except:
            strLink = ""
        strAddress = None
        try:
            strAddress = l['address_name']
        except:
            strAddress = ""
        strDescription = None
        try:
            strDescription = l['ads']['article']
        except:
            strAddress = ""

        u[strName] = [strLink, strAddress, strDescription]
    return u

def parseResponsePlaces(text):
    dic = json.loads(text)
    o = dic.get('result')

    for i in o.get('items'):
        l = dict(i)
        strName = l['name']
        strAddress = None
        try:
            strAddress = l['address_name']
        except:
            strAddress = ""
        if (strAddress != ""):
            u[strName] = [strAddress]
    return u


def parseResponseCoordsByAddress(text, userLat, userLong):
    dic = json.loads(text)
    o = dic.get('result')
    addresses = o.get('items')
    # Так как в отправляемом адресе нет названия города, то api может отправить несколькоо координат и надо выбрать ближайшую
    resLat = addresses[0]['point']['lat']
    resLong = addresses[0]['point']['lon']
    minDistance = math.sqrt((addresses[0]['point']['lat'] - userLat)*(addresses[0]['point']['lat'] - userLat) +
                       (addresses[0]['point']['lon'] - userLong)*(addresses[0]['point']['lon'] - userLong))
    for i in addresses:
        distance = math.sqrt((i['point']['lat'] - userLat)*(i['point']['lat'] - userLat) +
                       (i['point']['lon'] - userLong)*(i['point']['lon'] - userLong))
        if distance < minDistance:
            minDistance = distance
            resLat = i['point']['lat']
            resLong = i['point']['lon']

    lat = resLat
    long = resLong
    return [lat, long]

def sendButtonsCaffee(id, listResult):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for key, value in listResult.items():
        text = "Caffee: " + key
        item1 = types.KeyboardButton(text=text, )
        markup.add(item1)
    item2 = types.KeyboardButton("В начало")
    markup.add(item2)
    bot.send_message(id, 'Список ближайших к вам кафе', reply_markup=markup)

def sendButtonsPlaces(id, listResult):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for key, value in listResult.items():
        text = "Place: " + key
        item1 = types.KeyboardButton(text=text, )
        markup.add(item1)
    item2 = types.KeyboardButton("В начало")
    markup.add(item2)
    bot.send_message(id, 'Список ближайших к вам мест: ', reply_markup=markup)


# Запускаем бота
bot.polling(none_stop=True, interval=0)