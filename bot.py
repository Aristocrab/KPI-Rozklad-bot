from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import sqlite3
import logic


def timetable(update, context):
    context.bot.send_message(update.effective_chat.id, "_1 пара_  08-30 - 10-05\n"
                             + "_2 пара_  10-25 - 12-00\n"
                             + "_3 пара_  12-20 - 13-55\n"
                             + "_4 пара_  14-15 - 15-50\n"
                             + "_5 пара_  16-10 - 17-45", parse_mode='Markdown')


def r(update, context):
    if len(update.message.text) > len("/r "):
        group = logic.get_group_id(update.message.text[3:])
        if group != -1:
            context.bot.send_message(update.effective_chat.id, f"Групу змінено на *{update.message.text[3:]}*",
                                     parse_mode='Markdown')

            cursor.execute(f'INSERT or REPLACE INTO groups VALUES ({update.effective_chat.id}, {group}, NULL);')
            sqlite_connection.commit()
        else:
            context.bot.send_message(update.effective_chat.id, "Групу не знайдено", parse_mode='Markdown')
    else:
        context.bot.send_message(update.effective_chat.id, "Виберіть групу. Напр. /r бс-14", parse_mode='Markdown')


def select(update, context):
    if len(update.message.text) > len("/select "):
        groups_list = update.message.text[8:].replace(",", "").split(" ")
        groups_id_list = []
        ret_message = "Групи "

        if len(groups_list) > 0:
            if len(groups_list) == 1:
                context.bot.send_message(update.effective_chat.id,
                                         "Для обрання своєї групи використовуйте напр. /r да-11",
                                         parse_mode='Markdown')
                return

            for group in groups_list:
                group_id = logic.get_group_id(group)
                if group_id == -1:
                    context.bot.send_message(update.effective_chat.id, f"Групи *{group}* не знайдено",
                                             parse_mode='Markdown')
                    return
                groups_id_list.append(group_id)
                ret_message += f"*{group}*, "

            ret_message = ret_message[:-2]
            ret_message += " додано"
            context.bot.send_message(update.effective_chat.id, ret_message, parse_mode='Markdown')

        pref = " ".join(map(str, groups_id_list))
        comm = f"UPDATE groups SET prefered_groups = '{pref}' WHERE user_id = {update.effective_chat.id}"
        cursor.execute(comm)
        sqlite_connection.commit()

    else:
        context.bot.send_message(update.effective_chat.id,
                                 "Ви можете обрати декілька груп, щоб зручно дивитися збіг розкладів. "
                                 "Напр. /select да-11 іс-12 бс-14",
                                 parse_mode='Markdown')


def selections(update, context):
    cursor.execute(f'SELECT prefered_groups FROM groups WHERE user_id = {update.effective_chat.id};')
    prefered_groups = cursor.fetchone()
    if prefered_groups is not None:
        context.bot.send_message(update.effective_chat.id, prefered_groups[0], parse_mode='Markdown')


def schedule(update, context):
    cursor.execute(f'SELECT group_id FROM groups WHERE user_id = {update.effective_chat.id};')
    group = cursor.fetchone()
    if group is not None:
        if update.message.text == "/today" or update.message.text == "/t":
            context.bot.send_message(update.effective_chat.id, logic.get_lessons_for_today(group[0]),
                                     parse_mode='Markdown')
        elif update.message.text == "/tomorrow" or update.message.text == "/tm":
            context.bot.send_message(update.effective_chat.id, logic.get_lessons_for_tomorrow(group[0]),
                                     parse_mode='Markdown')
        elif update.message.text == "/week" or update.message.text == "/w":
            context.bot.send_message(update.effective_chat.id, logic.get_lessons_for_this_week(group[0]),
                                     parse_mode='Markdown')
        elif update.message.text == "/nextweek" or update.message.text == "/nw":
            context.bot.send_message(update.effective_chat.id, logic.get_lessons_for_next_week(group[0]),
                                     parse_mode='Markdown')
        elif update.message.text == "/full" or update.message.text == "/f":
            this_week = logic.get_lessons_for_this_week(group[0], full=True)
            next_week = logic.get_lessons_for_next_week(group[0], full=True)

            context.bot.send_message(update.effective_chat.id, this_week, parse_mode='Markdown')
            context.bot.send_message(update.effective_chat.id, next_week, parse_mode='Markdown')
        elif update.message.text == "/who":
            context.bot.send_message(update.effective_chat.id, logic.get_teachers_name(group[0]), parse_mode='Markdown')
    else:
        context.bot.send_message(update.effective_chat.id, "Сперше оберіть групу через /r. Напр. /r да-11",
                                 parse_mode='Markdown')


if __name__ == "__main__":
    print("Bot started")

    updater = Updater(token="1840339382:AAEJmiBJh457AtDKMeuhk4QgALGv6iMgtdo", use_context=True)

    updater.dispatcher.add_handler(CommandHandler('timetable', timetable))
    updater.dispatcher.add_handler(CommandHandler('r', r))
    updater.dispatcher.add_handler(CommandHandler('select', select))
    updater.dispatcher.add_handler(CommandHandler('selections', selections))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.command, schedule))

    sqlite_connection = sqlite3.connect('user_groups.db', check_same_thread=False)
    cursor = sqlite_connection.cursor()
    cursor.execute('CREATE TABLE if not exists '
                   'groups (user_id INTEGER PRIMARY KEY, group_id INTEGER, prefered_groups TEXT);')

    updater.start_polling()
