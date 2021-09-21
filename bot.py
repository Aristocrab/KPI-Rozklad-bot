from telegram.ext import Updater, CommandHandler
import sqlite3
import logic

updater = Updater(token="1840339382:AAEJmiBJh457AtDKMeuhk4QgALGv6iMgtdo", use_context=True)
dispatcher = updater.dispatcher


def message_handler(command):
    def decorator(function):
        def wrapper():
            global dispatcher
            handler = CommandHandler(command, function)
            dispatcher.add_handler(handler)

        wrapper()

    return decorator


@message_handler(command="r")
def r(update, context):
    if update.message.text.startswith("/r "):
        group = logic.get_group_id(update.message.text)
        if group != -1:
            context.bot.send_message(update.effective_chat.id, f"Групу змінено на *{update.message.text[3:]}*",
                                     parse_mode='Markdown')

            cursor.execute(f'INSERT or REPLACE INTO groups VALUES ({update.effective_chat.id}, {group});')
            sqlite_connection.commit()
        else:
            context.bot.send_message(update.effective_chat.id, "Групу не знайдено", parse_mode='Markdown')
    else:
        context.bot.send_message(update.effective_chat.id, "Виберіть групу: /r бс-14", parse_mode='Markdown')


@message_handler(command="today")
def today(update, context):
    cursor.execute(f'SELECT group_id FROM groups WHERE user_id = {update.effective_chat.id};')
    group = cursor.fetchone()[0]

    context.bot.send_message(update.effective_chat.id, logic.get_lessons_for_today(group),
                             parse_mode='Markdown')


@message_handler(command="tomorrow")
def tomorrow(update, context):
    cursor.execute(f'SELECT group_id FROM groups WHERE user_id = {update.effective_chat.id};')
    group = cursor.fetchone()[0]

    context.bot.send_message(update.effective_chat.id, logic.get_lessons_for_tomorrow(group),
                             parse_mode='Markdown')


@message_handler(command="week")
def week(update, context):
    cursor.execute(f'SELECT group_id FROM groups WHERE user_id = {update.effective_chat.id};')
    group = cursor.fetchone()[0]

    context.bot.send_message(update.effective_chat.id, logic.get_lessons_for_this_week(group),
                             parse_mode='Markdown')


@message_handler(command="nextweek")
def nextweek(update, context):
    cursor.execute(f'SELECT group_id FROM groups WHERE user_id = {update.effective_chat.id};')
    group = cursor.fetchone()[0]

    context.bot.send_message(update.effective_chat.id, logic.get_lessons_for_next_week(group),
                             parse_mode='Markdown')


@message_handler(command="full")
def full(update, context):
    cursor.execute(f'SELECT group_id FROM groups WHERE user_id = {update.effective_chat.id};')
    group = cursor.fetchone()[0]

    this_week = logic.get_lessons_for_this_week(group, full=True)
    next_week = logic.get_lessons_for_next_week(group, full=True)

    context.bot.send_message(update.effective_chat.id, this_week, parse_mode='Markdown')
    context.bot.send_message(update.effective_chat.id, next_week, parse_mode='Markdown')


@message_handler(command="who")
def who(update, context):
    cursor.execute(f'SELECT group_id FROM groups WHERE user_id = {update.effective_chat.id};')
    group = cursor.fetchone()[0]

    context.bot.send_message(update.effective_chat.id, logic.get_teachers_name(group), parse_mode='Markdown')


@message_handler(command="timetable")
def timetable(update, context):
    context.bot.send_message(update.effective_chat.id, "_1 пара_  08-30 - 10-05\n"
                             + "_2 пара_  10-25 - 12-00\n"
                             + "_3 пара_  12-20 - 13-55\n"
                             + "_4 пара_  14-15 - 15-50\n"
                             + "_5 пара_  16-10 - 17-45", parse_mode='Markdown')


if __name__ == "__main__":
    print("Bot started")
    sqlite_connection = sqlite3.connect('user_groups.db', check_same_thread=False)
    cursor = sqlite_connection.cursor()
    cursor.execute('CREATE TABLE if not exists groups (user_id INTEGER PRIMARY KEY, group_id INTEGER);')
    updater.start_polling()
