# HotTour Readable. File into table.
import pandas as pd


def check_city(city_name):
    if not city_name or not isinstance(city_name, str):
        return False

    allowed_chars = {
        '-', "'", '.', ',', ' '
    }

    has_letter = False
    length = 0

    for char in city_name:
        if char not in allowed_chars and char.isalpha() == False:
            return False
        if char.isalpha():
            has_letter = True
        length += 1

    return has_letter and length >= 2


def check_time(s):
    if len(s) != 5 or s[2] != ':':
        return False
    
    hours, minutes = s.split(':')
    
    return (hours.isdigit() and minutes.isdigit() and
            0 <= int(hours) <= 23 and
            0 <= int(minutes) <= 59)


def check_date(s):
    s = s.strip() 
    try:
        num = float(s)
        if '.' in s:
            return True
        else:
            return False
    except ValueError:
        return False

try:
    with open('file.txt', 'r', encoding='utf-8') as file:
        lines = [line.rstrip('\n') for line in file]
        print(f"Прочитано {len(lines)} строк")

except FileNotFoundError:
    print("Файл не найден")
except UnicodeDecodeError:
    print("Ошибка кодировки файла")
except Exception as e:
    print(f"Произошла ошибка: {str(e)}")

fields = []
for f in range(len(lines) // 3):
    field = {
                'date_in': None,                      # заезд
                'hotel': None,                        # отель
                'nights': None,                       # количество ночей
                'typeof': None,                       # тип проживания
                'cost': None,                         # цена
                'airline_to': None,                   # авиакомпания
                'airline_from': None,                 # авиакомпания обратно
                'destinations_to': [None, None],      # путь следования(из, в) 
                'destinations_from': [None, None],    # путь следования(из, в) обратно
                'time_to': [None, None],              # время(взлет, посадка) перелета прибытия
                'time_from': [None, None],            # время(взлет, посадка) перелета отбытия
                'departure': None,                    # отбытие обратно
                'arrive': None                        # прибытие 
            }
    for i in range(3):
        index = f * 3 + i
        if i % 3 == 0 and check_date(lines[index].split(", ")[0]):
            cur_line = lines[index].split(", ")
            field['date_in'] = cur_line[0]
            field['nights'] = cur_line[1]
            field['hotel'] = cur_line[2]
            field['typeof'] = cur_line[3]
            field['cost'] = cur_line[4]
        else:
            flag = 0
            cur_line = lines[index].split(" ")
            for j in range(len(cur_line)):
                if cur_line[j] == '→':
                        flag = 1
                if i % 3 == 1:
                    if j == 0 and cur_line[j].isalpha():
                        field['airline_to'] = cur_line[j]
                    elif check_date(cur_line[j]):
                        field['arrive'] = cur_line[j]
                    elif check_time(cur_line[j]):
                        if field['time_to'][flag] == None:
                            field['time_to'][flag] = cur_line[j]
                    elif check_city(cur_line[j]):
                        if field['destinations_to'][flag] == None:
                            field['destinations_to'][flag] = cur_line[j]
                        else:
                            field['destinations_to'][flag] += " " + cur_line[j]
                if i % 3 == 2:
                    if j == 0 and cur_line[j].isalpha():
                        field['airline_from'] = cur_line[j]
                    elif check_date(cur_line[j]):
                        field['departure'] = cur_line[j]
                    elif check_time(cur_line[j]):
                        if field['time_from'][flag] == None:
                            field['time_from'][flag] = cur_line[j]
                    elif check_city(cur_line[j]):
                        if field['destinations_from'][flag] == None:
                            field['destinations_from'][flag] = cur_line[j]
                        else:
                            field['destinations_from'][flag] += " " + cur_line[j]
    fields.append(field)

for i in range(len(fields)):
    print(fields[i])

tours = []
for i in range(len(fields)):
    tour = {'Отель': fields[i]['hotel'], 'Дата заезда': fields[i]['date_in'], 'Кол-во ночей': fields[i]['nights'],
            'Проживание': fields[i]['typeof'], 'Авиакомпания туда': fields[i]['airline_to'], 'Дата туда': fields[i]['arrive'],
            'Время вылета туда': fields[i]['time_to'][0], 'Город вылета туда': fields[i]['destinations_to'][0],
            'Время прилета туда': fields[i]['time_to'][1], 'Город прилета туда': fields[i]['destinations_to'][1],
            'Авиакомпания обратно': fields[i]['airline_from'], 'Дата обратно': fields[i]['departure'],
            'Время вылета обратно': fields[i]['time_from'][0], 'Город вылета обратно': fields[i]['destinations_from'][0],
            'Время прилета обратно': fields[i]['time_from'][1], 'Город прилета обратно': fields[i]['destinations_from'][1],
            'Цена': fields[i]['cost']}
    tours.append(tour)

df = pd.DataFrame(tours)
with pd.ExcelWriter('HotTours.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False)

    worksheet = writer.sheets['Sheet1']
    for idx, col in enumerate(df.columns):
        max_len = max(
            df[col].astype(str).map(len).max(),
            len(str(col)))
        worksheet.set_column(idx, idx, max_len + 2)
