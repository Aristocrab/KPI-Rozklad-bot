from datetime import datetime, time
import requests

def get_lessons_for_today(group_id):
    return get_lessons_for_day(group_id, day_number = (datetime.today().weekday() + 1), day = "Сьогодні")
def get_lessons_for_tomorrow(group_id):
    if(datetime.today().weekday() + 1 == 7):
        return get_lessons_for_day(group_id, day_number = ((datetime.today().weekday() + 1) + 1) % 7, day = "Завтра", lesson_week = ["2", "1"][requests.get("https://api.rozklad.org.ua/v2/weeks").json()["data"] - 1])
    return get_lessons_for_day(group_id, day_number = ((datetime.today().weekday() + 1) + 1) % 7, day = "Завтра")


def get_lessons_for_day(group_id, day_number, day, lesson_week = str(requests.get("https://api.rozklad.org.ua/v2/weeks").json()["data"])):
    url = "https://api.rozklad.org.ua/v2/groups/"
    request_url = url + str(group_id) + "/lessons?filter={'day_number':" + str(day_number) + ",'lesson_week':" + lesson_week + "}"
    request = requests.get(request_url)
    if(request.status_code != 200):
        return f"{day} пар немає"
    response = request.json()["data"]
    lessons = ""
    lessons += f'*{response[0]["day_name"]}* ({lesson_week})\n'

    for i in range(len(response)):
        lessons += response[i]["lesson_number"] + ") " + response[i]["lesson_name"] + " `" + response[i]["lesson_type"] + " " + response[i]["rooms"][0]["room_name"] + "`\n"

    return lessons


def get_teachers_name(group_id):
    url = "https://api.rozklad.org.ua/v2/groups/"
    request_url = url + str(group_id) + "/lessons?filter={'day_number':" + str(datetime.today().weekday() + 1) + ",'lesson_week':" + str(requests.get("https://api.rozklad.org.ua/v2/weeks").json()["data"]) + "}"
    request = requests.get(request_url)
    if(request.status_code != 200):
        return f"Сьогодні пар немає"
    response = request.json()["data"]
    
    now = datetime.now().time()
    current_lesson = get_lesson(now)
    current_break = get_break(now)
    name = ""
    
    if(current_lesson != -1):
        for teacher in response[current_lesson]["teachers"]:
            name += teacher["teacher_full_name"] + "\n"
    elif(current_break != -1):
        name += f"Попередня ({current_break + 1}-а) пара:"
        for teacher in response[current_break]["teachers"]:
            name += teacher["teacher_full_name"] + "\n"
        
        name += "\n"

        name += f"Наступна ({current_break + 1}-а) пара:"
        for teacher in response[current_break+1]["teachers"]:
            name += teacher["teacher_full_name"] + "\n"

    return name


def get_lesson(current_time):
    lessons = [
        [time(8, 30), time(10, 5)],
        [time(10, 25), time(12, 0)],
        [time(12, 20), time(13, 55)],
        [time(14, 15), time(15, 50)],
        [time(16, 10), time(17, 45)],
    ]
    if time(8, 0) <= current_time <= lessons[0][1]:
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
        [time(10, 5), time(10, 25)],
        [time(12, 0), time(12, 20)],
        [time(13, 55), time(14, 15)],
        [time(15, 50), time(16, 10)],
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


def get_lessons_for_this_week(group_id, full = False):
    return get_lessons_for_week(group_id, lesson_week = 2 - datetime.today().isocalendar().week % 2, full = full)
def get_lessons_for_next_week(group_id, full = False):
    return get_lessons_for_week(group_id, lesson_week = 2 - abs(datetime.today().isocalendar().week % 2 - 1), full = full)


def get_lessons_for_week(group_id, lesson_week, full = False):
    url = "https://api.rozklad.org.ua/v2/groups/"
    request_url = url + str(group_id) + "/lessons?filter={'lesson_week':" + str(lesson_week) + "}"
    request = requests.get(request_url)
    response = request.json()["data"]
    day_name = ""
    lessons = ""

    for i in range(len(response)):
        if(day_name != response[i]["day_name"]):
            day_name = response[i]["day_name"]
            if(i > 0):
                lessons += "\n"
            lessons += f'*{day_name}*\n'

        lessons += response[i]["lesson_number"] + ") " + response[i]["lesson_name"] + " `" + response[i]["lesson_type"] + " " + response[i]["rooms"][0]["room_name"] + "`\n"
        if(full):
            lessons += "     " + response[i]["teacher_name"] + "\n"

    lessons = "*" + ["Перша", "Друга"][lesson_week - 1] + " неділя*\n" + lessons
    return lessons