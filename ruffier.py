txt_index = "Ваш индекс Руфье: "
txt_workheart = "Работоспособность сердца: "
txt_nodata = '''
нет данных для такого возраста'''
txt_res = []
txt_res.append('''низкая. 
Срочно запишитесь на тренировку!
Рекомендации: Начните с ходьбы!''')
txt_res.append('''удовлетворительная. 
С этим нужно что-то делать!
Рекомендации: Регулярные тренировки 2-3 раза в неделю''')
txt_res.append('''средняя. 
Неплохо, но есть куда расти!
Рекомендации: Увеличьте кардионагрузки!''')
txt_res.append('''выше среднего.
Вы - элитный спортсмен. Ещё немного и вы - легенда!
Рекомендации: Поддерживайте текущий уровень!''')
txt_res.append('''высокая.
Вы - легендарный спортсмен! Так держать!
Рекомендация: Участвуйте в соревнованиях!''')


def ruffier_index(P1, P2, P3):
    ''' возвращает значение индекса по трем показателям пульса для сверки с таблицей'''
    return (4 * (P1 + P2 + P3) - 200) / 10


def get_age_level(age):
    if age < 7:
        return None
    elif age <= 15:
        norm_age = (age - 7) // 2
        return 21 - norm_age * 1.5
    else:
        return 15


def interpret_ruffier_result(r_index, age):
    border = get_age_level(age)
    if border is None:
        return None
    if r_index >= border:
        return 0
    elif r_index >= border - 4:
        return 1
    elif r_index >= border - 9:
        return 2
    elif r_index >= border - 14.5:
        return 3
    else:
        return 4


def format_result(P1, P2, P3, age):
    if age < 7:
        return f"{txt_index} 0 {txt_nodata}"

    r_index = ruffier_index(P1, P2, P3)
    level = interpret_ruffier_result(r_index, age)

    if level is not None:
        result_text = txt_res[level]
        return f"{txt_index}{r_index:.1f}\n{txt_workheart}{result_text}"
    else:
        return f"{txt_index}{r_index:.1f}\n{txt_workheart}. Не удалось определить уровень"
