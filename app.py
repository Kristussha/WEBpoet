from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import numpy as np
from init_db import init_db, get_db_connection

app = Flask(__name__)

# Список месяцев для отображения
MONTHS = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
]


@app.route('/')
def index():
    return render_template('index.html')


# Управление поэтами
@app.route('/poets')
def poets():
    conn = get_db_connection()
    poets = conn.execute('SELECT * FROM poets').fetchall()
    conn.close()
    return render_template('poets.html', poets=poets)


@app.route('/add_poet', methods=['POST'])
def add_poet():
    name = request.form['name']
    age = request.form['age']
    city = request.form['city']
    conn = get_db_connection()
    conn.execute('INSERT INTO poets (name, age, city) VALUES (?, ?, ?)', (name, age, city))
    conn.commit()
    conn.close()
    return redirect(url_for('poets'))


@app.route('/delete_poet/<int:id>')
def delete_poet(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM poets WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('poets'))


# Управление работами
@app.route('/works')
def works():
    conn = get_db_connection()
    works = conn.execute(
        'SELECT works.id, works.title, works.text, works.year, poets.name FROM works JOIN poets ON works.poet_id = poets.id').fetchall()
    poets = conn.execute('SELECT id, name FROM poets').fetchall()
    conn.close()
    return render_template('works.html', works=works, poets=poets)


@app.route('/add_work', methods=['POST'])
def add_work():
    title = request.form['title']
    text = request.form['text']
    year = request.form['year']
    poet_id = request.form['poet_id']
    conn = get_db_connection()
    conn.execute('INSERT INTO works (title, text, year, poet_id) VALUES (?, ?, ?, ?)', (title, text, year, poet_id))
    conn.commit()
    conn.close()
    return redirect(url_for('works'))


@app.route('/delete_work/<int:id>')
def delete_work(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM works WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('works'))


# Управление выступлениями
@app.route('/performances')
def performances():
    conn = get_db_connection()
    performances = conn.execute(
        'SELECT performances.id, poets.name, performances.theme, performances.date, performances.performance_order FROM performances JOIN poets ON performances.poet_id = poets.id').fetchall()
    poets = conn.execute('SELECT id, name FROM poets').fetchall()
    conn.close()
    return render_template('performances.html', performances=performances, poets=poets)


@app.route('/add_performance', methods=['POST'])
def add_performance():
    poet_id = request.form['poet_id']
    theme = request.form['theme']
    date = request.form['date']
    performance_order = request.form['performance_order']
    conn = get_db_connection()
    conn.execute('INSERT INTO performances (poet_id, theme, date, performance_order) VALUES (?, ?, ?, ?)',
                 (poet_id, theme, date, performance_order))
    conn.commit()
    conn.close()
    return redirect(url_for('performances'))


@app.route('/delete_performance/<int:id>')
def delete_performance(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM performances WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('performances'))


# Анализ конкурсов
@app.route('/contests')
def contests():
    conn = get_db_connection()
    contests = conn.execute('SELECT * FROM contests').fetchall()
    attendance = conn.execute('SELECT * FROM attendance').fetchall()
    conn.close()
    return render_template('contests.html', contests=contests, attendance=attendance, months=MONTHS)


@app.route('/add_contest', methods=['POST'])
def add_contest():
    try:
        month = int(request.form['month'])
        # Валидация месяца
        if month < 1 or month > 12:
            return "Ошибка: месяц должен быть в диапазоне от 1 до 12", 400
        # Проверка на существование записи для данного месяца
        conn = get_db_connection()
        existing = conn.execute('SELECT COUNT(*) FROM attendance WHERE month = ?', (month,)).fetchone()[0]
        if existing > 0:
            return "Ошибка: данные для этого месяца уже существуют", 400
    except ValueError:
        return "Ошибка: месяц должен быть числом", 400

    theme = request.form['theme']
    works_count = request.form['works_count']
    visitors = request.form['visitors']
    participants = request.form['participants']
    conn = get_db_connection()
    conn.execute('INSERT INTO contests (month, theme, works_count) VALUES (?, ?, ?)', (month, theme, works_count))
    conn.execute('INSERT INTO attendance (month, visitors, participants) VALUES (?, ?, ?)',
                 (month, visitors, participants))
    conn.commit()
    conn.close()
    return redirect(url_for('contests'))


# Прогнозирование
@app.route('/forecast')
def forecast():
    conn = get_db_connection()
    # Фильтруем только записи с корректными значениями month (1-12)
    attendance = conn.execute(
        'SELECT month, visitors, participants FROM attendance WHERE month BETWEEN 1 AND 12 ORDER BY month').fetchall()
    conn.close()

    if not attendance:
        return render_template('forecast.html',
                               error="Нет данных о посещаемости. Пожалуйста, добавьте данные о конкурсах на странице 'Конкурсы'.")

    # Удаляем дубликаты, сохраняя последнюю запись для каждого месяца
    unique_attendance = {}
    for record in attendance:
        unique_attendance[record['month']] = record
    attendance = list(unique_attendance.values())

    # Подготовка данных
    df = pd.DataFrame(attendance, columns=['month', 'visitors', 'participants'])

    # Параметры скользящей средней
    window_size = 3  # Размер окна

    # Расчёт прогнозных значений и ошибок
    forecast_data = []
    actual_visitors = df['visitors'].tolist()
    forecast_visitors = []

    # Первые (window_size-1) значения не могут быть спрогнозированы
    for i in range(window_size - 1):
        forecast_visitors.append(None)

    # Расчёт скользящей средней для каждого месяца
    for i in range(window_size - 1, len(df)):
        window_values = df['visitors'].iloc[i - window_size + 1:i + 1].values
        forecast_value = window_values.mean()
        forecast_visitors.append(forecast_value)

    # Расчёт ошибок
    for i in range(len(df)):
        actual = actual_visitors[i]
        forecast = forecast_visitors[i]
        if forecast is not None:
            absolute_error = abs(actual - forecast)
            relative_error = absolute_error / actual if actual != 0 else 0
        else:
            absolute_error = None
            relative_error = None
        forecast_data.append({
            'month': MONTHS[df['month'].iloc[i] - 1],  # Используем значение month из данных
            'actual': actual,
            'forecast': round(forecast, 2) if forecast is not None else None,
            'absolute_error': round(absolute_error, 2) if absolute_error is not None else None,
            'relative_error': round(relative_error, 2) if relative_error is not None else None
        })

    # Прогноз на следующие два месяца (ноябрь и декабрь, если данных меньше 12)
    next_months_forecast = []
    if len(df) >= window_size:
        for i in range(len(df), min(len(df) + 2, 12)):  # Прогноз на 11 и 12 месяц
            if i < len(MONTHS):
                window_values = df['visitors'].iloc[i - window_size:i].values
                forecast_value = window_values.mean()
                next_months_forecast.append({
                    'month': MONTHS[i],
                    'forecast': round(forecast_value, 2)
                })

    # Данные для графика
    chart_labels = [MONTHS[m - 1] for m in df['month']]
    chart_actual = actual_visitors
    chart_forecast = [f if f is not None else None for f in forecast_visitors]

    # Статистика ошибок
    absolute_errors = [d['absolute_error'] for d in forecast_data if d['absolute_error'] is not None]
    relative_errors = [d['relative_error'] for d in forecast_data if d['relative_error'] is not None]
    avg_absolute_error = round(np.mean(absolute_errors), 6) if absolute_errors else 0
    avg_relative_error = round(np.mean(relative_errors), 3) if relative_errors else 0

    return render_template(
        'forecast.html',
        forecast_data=forecast_data,
        next_months_forecast=next_months_forecast,
        chart_labels=chart_labels,
        chart_actual=chart_actual,
        chart_forecast=chart_forecast,
        avg_absolute_error=avg_absolute_error,
        avg_relative_error=avg_relative_error,
        months=MONTHS
    )


# Маршрут для поиска поэта
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return render_template('search.html', poets=None, query=query,
                               error="Пожалуйста, введите фамилию поэта для поиска.")

    conn = get_db_connection()
    # Ищем поэта по фамилии с использованием DISTINCT для исключения дубликатов
    poets = conn.execute(
        "SELECT DISTINCT * FROM poets WHERE name LIKE ?",
        ('%' + query + '%',)
    ).fetchall()

    if not poets:
        conn.close()
        return render_template('search.html', poets=None, query=query, error="Поэт с такой фамилией не найден.")

    # Для каждого найденного поэта извлекаем его произведения и выступления
    poet_data = []
    seen_poets = set()  # Для отслеживания уникальных поэтов по id
    for poet in poets:
        poet_id = poet['id']
        if poet_id in seen_poets:
            continue  # Пропускаем дубликаты
        seen_poets.add(poet_id)

        # Извлекаем произведения с DISTINCT
        works = conn.execute(
            "SELECT DISTINCT title, text, year FROM works WHERE poet_id = ?",
            (poet_id,)
        ).fetchall()

        # Извлекаем выступления с DISTINCT
        performances = conn.execute(
            "SELECT DISTINCT theme, date, performance_order FROM performances WHERE poet_id = ?",
            (poet_id,)
        ).fetchall()

        poet_data.append({
            'poet': poet,
            'works': works,
            'performances': performances
        })

    conn.close()
    return render_template('search.html', poet_data=poet_data, query=query)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)