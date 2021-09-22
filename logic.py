import datetime
import urllib.parse

import requests


def get_group_id(text):
    url = "https://api.rozklad.org.ua/v2/groups/?search={%27query%27:%27" + urllib.parse.quote(text) + "%27}"
    request = requests.get(url)

    if request.status_code != 200:
        return -1

    return request.json()["data"][0]["group_id"]


def get_lessons_for_today(group_id):
    return get_lessons_for_day(group_id, day_number=(datetime.datetime.today().weekday() + 1), day="Сьогодні")


def get_lessons_for_tomorrow(group_id):
    if datetime.datetime.today().weekday() + 1 == 7:
        return get_lessons_for_day(group_id, day_number=((datetime.datetime.today().weekday() + 1) + 1) % 7,
                                   day="Завтра", lesson_week=["2", "1"][
                requests.get("https://api.rozklad.org.ua/v2/weeks").json()["data"] - 1])

    return get_lessons_for_day(group_id, day_number=((datetime.datetime.today().weekday() + 1) + 1) % 7, day="Завтра")


def get_lessons_for_day(group_id, day_number, day,
                        lesson_week=str(requests.get("https://api.rozklad.org.ua/v2/weeks").json()["data"])):
    url = "https://api.rozklad.org.ua/v2/groups/"

    request_url = url + str(group_id) + "/lessons?filter={'day_number':" + str(
        day_number) + ",'lesson_week':" + lesson_week + "}"
    request = requests.get(request_url)
    if request.status_code != 200:
        return f"{day} пар немає"
    response = request.json()["data"]
    lessons = ""
    lessons += f'*{response[0]["day_name"]}* ({lesson_week})\n'

    for i in range(len(response)):
        if len(response[i]["rooms"]) != 0:
            lessons += response[i]["lesson_number"] + ") " + response[i]["lesson_name"] + " `" + response[i][
                "lesson_type"] + " " + response[i]["rooms"][0]["room_name"] + "`\n"
        else:
            lessons += response[i]["lesson_number"] + ") " + response[i]["lesson_name"] + " `" + response[i][
                "lesson_type"] + "`\n"

    return lessons


def get_lessons_for_this_week(group_id, full=False):
    return get_lessons_for_week(group_id,
                                lesson_week=requests.get("https://api.rozklad.org.ua/v2/weeks").json()["data"],
                                full=full)


def get_lessons_for_next_week(group_id, full=False):
    return get_lessons_for_week(group_id, lesson_week=(requests.get("https://api.rozklad.org.ua/v2/weeks")
                                                       .json()["data"] + 1) % 2, full=full)


def get_lessons_for_week(group_id, lesson_week, full=False):
    url = "https://api.rozklad.org.ua/v2/groups/"
    request_url = url + str(group_id) + "/lessons?filter={'lesson_week':" + str(lesson_week) + "}"
    request = requests.get(request_url)
    response = request.json()["data"]
    day_name = ""
    lessons = ""

    for i in range(len(response)):
        if day_name != response[i]["day_name"]:
            day_name = response[i]["day_name"]
            if i > 0:
                lessons += "\n"
            lessons += f'*{day_name}*\n'

        if len(response[i]["rooms"]) != 0:
            lessons += response[i]["lesson_number"] + ") " + response[i]["lesson_name"] + " `" + response[i][
                "lesson_type"] + " " + response[i]["rooms"][0]["room_name"] + "`\n"
        else:
            lessons += response[i]["lesson_number"] + ") " + response[i]["lesson_name"] + " `" + response[i][
                "lesson_type"] + "`\n"
        if full:
            lessons += "     " + response[i]["teacher_name"] + "\n"

    lessons = "*" + ["Перша", "Друга"][lesson_week - 1] + " неділя*\n" + lessons
    return lessons


def get_teachers_name(group_id):
    url = "https://api.rozklad.org.ua/v2/groups/"
    request_url = url + str(group_id) + "/lessons?filter={'day_number':" + str(
        datetime.datetime.today().weekday() + 1) + ",'lesson_week':" + str(
        requests.get("https://api.rozklad.org.ua/v2/weeks").json()["data"]) + "}"
    request = requests.get(request_url)
    if request.status_code != 200:
        return f"Сьогодні пар немає"
    response = request.json()["data"]

    now = datetime.datetime.now().time()
    current_lesson = get_lesson(now)
    current_break = get_break(now)
    name = ""

    if current_lesson != -1:
        for lesson in response:
            if lesson["lesson_number"] == str(current_lesson):
                for teacher in lesson["teachers"]:
                    name += teacher["teacher_name"].replace("посада ", "").replace("викладач ", "") + "\n"
    elif current_break != -1:
        name += f"*Попередня ({current_break}-а) пара:*"
        for lesson in response:
            if lesson["lesson_number"] == str(current_break):
                for teacher in lesson["teachers"]:
                    name += teacher["teacher_name"].replace("посада ", "").replace("викладач ", "") + "\n"

        name += "\n"

        name += f"*Наступна ({current_break + 1}-а) пара:*"
        for lesson in response:
            if lesson["lesson_number"] == str(current_break+1):
                for teacher in lesson["teachers"]:
                    name += teacher["teacher_name"].replace("посада ", "").replace("викладач ", "") + "\n"
    else:
        return "Зараз уроку немає"

    return name


# Utils
def get_lesson(current_time):
    lessons = [
        [datetime.time(8, 30), datetime.time(10, 5)],
        [datetime.time(10, 25), datetime.time(12, 0)],
        [datetime.time(12, 20), datetime.time(13, 55)],
        [datetime.time(14, 15), datetime.time(15, 50)],
        [datetime.time(16, 10), datetime.time(17, 45)],
    ]
    if datetime.time(8, 0) <= current_time <= lessons[0][1]:
        return 0
    elif lessons[1][0] <= current_time <= lessons[1][1]:
        return 1
    elif lessons[2][0] <= current_time <= lessons[2][1]:
        return 2
    elif lessons[3][0] <= current_time <= lessons[3][1]:
        return 3
    elif lessons[4][0] <= current_time <= lessons[4][1]:
        return 4
    return -1


def get_break(current_time):
    breaks = [
        [datetime.time(10, 5), datetime.time(10, 25)],
        [datetime.time(12, 0), datetime.time(12, 20)],
        [datetime.time(13, 55), datetime.time(14, 15)],
        [datetime.time(15, 50), datetime.time(16, 10)],
    ]
    if breaks[0][0] < current_time < breaks[0][1]:
        return 0
    elif breaks[1][0] <= current_time <= breaks[1][1]:
        return 1
    elif breaks[2][0] <= current_time <= breaks[2][1]:
        return 2
    elif breaks[3][0] <= current_time <= breaks[3][1]:
        return 3
    return -1
