import telebot as tg
from weatherapi import API
from database import DB
import threading
import requests


#сервер-заглушка, хостинг back4app ругается если не запущено ничего на открытом порте. Также принимает запросы снаружи.
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
def run_server(server_class=TCPServer, handler_class=SimpleHTTPRequestHandler):
  server_address = ('', 3000)
  httpd = server_class(server_address, handler_class)
  try:
      httpd.serve_forever()
  except KeyboardInterrupt:
      httpd.server_close()
plug_thread = threading.Thread(target=run_server)
plug_thread.start()

#Ещё один класс, который имитирует активность чтобы хостинг не отрубил. Шлёт запросы наружу на один из серверов и на сервер созданный ранее.
class NO_SLEEP:
    def __init__(self) -> None:
        self.timer = threading.Timer(60, self.no_sleep_request)

    def no_sleep_request(self):
        requests.get("XXX")
        self.timer = threading.Timer(60, self.no_sleep_request)
no_sleep_timer = NO_SLEEP()


class PULSE:
    def __init__(self) -> None:
        self.pulsator_delay = 2
        self.database_API = DB()
        self.weather_API = API()
        self.timer = threading.Timer(self.pulsator_delay, self.check_database)
        self.timer.start()
    def check_database(self):
        user_to_mess = self.database_API.get_overtimed_users()
        for user_id, chat_id, city in user_to_mess:
            print(f"Send periodical to {chat_id} from {city}")
            periodical_message(chat_id, self.weather_API.get_weather(city))
            self.database_API.refresh_user_time(user_id)

        self.timer = threading.Timer(self.pulsator_delay, self.check_database)
        self.timer.start()


bot_acces_token = 'XXX'
bot = tg.TeleBot(bot_acces_token)
print("BOT CONNECTION SUCCES!")

def periodical_message(chat_id, text):
    bot.send_message(chat_id, text)

Weather_api = API()
Database_API = DB()
database_timer = PULSE() 

@bot.message_handler(commands=['unregister'])
def unregister_user(message):
    if Database_API.check_is_user_exists(message.from_user.id):
        Database_API.delete_user(message.from_user.id)
        bot.send_message(message.chat.id, "Вы отписались от рассылки!")
    else:
        bot.send_message(message.chat.id, "Упс! Вы не зарегистрированы!")

@bot.message_handler(commands=['register'])
def register_user(message):
    if Database_API.check_is_user_exists(message.from_user.id):
        bot.send_message(message.chat.id, "Упс! Вы уже зарегистрированы!")
    else:
        Database_API.create_new_user(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, "Вы успешно зарегистрированы!")

@bot.message_handler(commands=['start'])
def start_message(message):

    bot.send_message(message.chat.id,
    '''
    Бот, который высылает погоду раз в заданный промежуток времени.
    Команды: 
    /register - зарегистрироваться. Без этого команды кроме /start не будут работать.
    /interval - задать требуемый интервал. После отправки сообщения бот выдаст список значений на выбор. Стандартное значение - 12ч.
    /city - задать ваш город. По умолчанию - Москва
    /unregister - отписаться от рассылки

    P.S Бот отсчитывает время начиная от самого позднего из следующих событий: регистрация, смена интервала времени, последняя отправка периодического сообщения.
    Возможны небольшие задержки при работе, но не более 2-3 секунд, это связано с хостингом.
    '''
    )

@bot.message_handler(commands=['city'])
def set_city(message):
    if (message.text == '/city'):
        if not Database_API.check_is_user_exists(message.from_user.id):
            bot.send_message(message.chat.id, "Сначала зарегистрируйтесь!")
            return
        bot.send_message(message.chat.id, "Отправьте сообщение с названием города")
        bot.register_next_step_handler(message, add_city)
def add_city(message):
    if Weather_api.validate_city(message.text):
        Database_API.change_user_city(message.from_user.id, message.text)
        bot.send_message(message.chat.id, "Город успешно выбран!")
    else:
        bot.send_message(message.chat.id, "Некорректный город! Попробуйте выбрать другие с помощью /city.")

@bot.message_handler(commands=['interval'])
def set_interval(message):
    if (message.text == '/interval'):
        if not Database_API.check_is_user_exists(message.from_user.id):
            bot.send_message(message.chat.id, "Сначала зарегистрируйтесь!")
            return
        bot.send_message(message.chat.id, "Напишите желаемый интервал для отправки сводки о погоде, варианты: \n минута \n полчаса  \n час \n 12ч")
        bot.register_next_step_handler(message, add_interval)
def add_interval(message):
    valid_values = ['минута', 'полчаса', 'час', '12ч']
    valid_numeric_values = {
        'минута' : 60,
        'полчаса' : 1800,
        'час' : 3600,
        '12ч' : 43200
    }
    if message.text in valid_values:
        Database_API.change_user_interval(message.from_user.id, valid_numeric_values[message.text])
        Database_API.refresh_user_time(message.from_user.id)
        bot.send_message(message.chat.id, "Интервал времени успешно задан.")
    else:
        bot.send_message(message.chat.id, "Некорректное значение. Проверьте, что введенные вами данные соответствуют списку допустимых и не имеют лишних символов.")

bot.infinity_polling()
