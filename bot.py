import logic
import telebot

bot = telebot.TeleBot("1840339382:AAEJmiBJh457AtDKMeuhk4QgALGv6iMgtdo", parse_mode="MARKDOWN")


@bot.message_handler(commands=['today'])
def today(message):
    bot.send_message(message.chat.id, logic.get_lessons_for_today(708))


@bot.message_handler(commands=['tomorrow'])
def tomorrow(message):
    bot.send_message(message.chat.id, logic.get_lessons_for_tomorrow(708))


@bot.message_handler(commands=['week'])
def week(message):
    bot.send_message(message.chat.id, logic.get_lessons_for_this_week(708))


@bot.message_handler(commands=['nextweek'])
def nextweek(message):
    bot.send_message(message.chat.id, logic.get_lessons_for_next_week(708))


@bot.message_handler(commands=['full'])
def full(message):
    this_week = logic.get_lessons_for_this_week(708, full = True)
    next_week = logic.get_lessons_for_next_week(708, full = True)
    bot.send_message(message.chat.id, this_week)
    bot.send_message(message.chat.id, next_week)


@bot.message_handler(commands=['who'])
def who(message):
    bot.send_message(message.chat.id, logic.get_teachers_name(708))


@bot.message_handler(commands=['timetable'])
def timetable(message):
    bot.send_message(message.chat.id, "_1 пара_  08-30 - 10-05\n" 
        + "_2 пара_  10-25 - 12-00\n" 
        + "_3 пара_  12-20 - 13-55\n" 
        + "_4 пара_  14-15 - 15-50\n" 
        + "_5 пара_  16-10 - 17-45")


if __name__ == "__main__":
    print("Bot started")
    bot.polling()