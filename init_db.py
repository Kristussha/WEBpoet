import sqlite3


def init_db():
    conn = sqlite3.connect('poetry_contest.db')
    conn.execute('PRAGMA foreign_keys = ON')
    c = conn.cursor()

    # Создание таблицы poets с уникальным ограничением на name, age, city
    c.execute('''CREATE TABLE IF NOT EXISTS poets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        city TEXT,
        UNIQUE(name, age, city)
    )''')

    # Создание таблицы works с уникальным ограничением на poet_id, title, text, year
    c.execute('''CREATE TABLE IF NOT EXISTS works (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        text TEXT,
        year INTEGER,
        poet_id INTEGER,
        FOREIGN KEY (poet_id) REFERENCES poets(id) ON DELETE CASCADE,
        UNIQUE(poet_id, title, text, year)
    )''')

    # Создание таблицы performances с уникальным ограничением на poet_id, theme, date, performance_order
    c.execute('''CREATE TABLE IF NOT EXISTS performances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poet_id INTEGER,
        theme TEXT,
        date TEXT,
        performance_order INTEGER,
        FOREIGN KEY (poet_id) REFERENCES poets(id) ON DELETE CASCADE,
        UNIQUE(poet_id, theme, date, performance_order)
    )''')

    # Создание таблицы contests
    c.execute('''CREATE TABLE IF NOT EXISTS contests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month INTEGER NOT NULL,
        theme TEXT,
        works_count INTEGER
    )''')

    # Создание таблицы attendance
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month INTEGER NOT NULL,
        visitors INTEGER,
        participants INTEGER
    )''')

    # Вставка тестовых данных для poets
    poets = [
        ('Анна Иванова', 25, 'Москва'),
        ('Борис Петров', 30, 'Санкт-Петербург'),
        ('Елена Смирнова', 22, 'Екатеринбург'),
        ('Дмитрий Козлов', 35, 'Новосибирск'),
        ('Мария Соколова', 28, 'Казань')
    ]
    c.executemany('INSERT OR IGNORE INTO poets (name, age, city) VALUES (?, ?, ?)', poets)

    # Вставка тестовых данных для works
    works = [
        ('Свет луны', 'В ночи сияет свет луны...', 2022, 1),
        ('Город спит', 'Город спит под звёздным небом...', 2023, 1),
        ('Морской бриз', 'Волны шепчут о свободе...', 2021, 2),
        ('Песнь ветра', 'Ветер в поле напевает...', 2023, 2),
        ('Рассвет', 'Утро красит небо в розовый...', 2022, 3),
        ('Зимний сон', 'Снег ложится мягким покрывалом...', 2023, 4),
        ('Путь домой', 'Дорога вьётся меж холмов...', 2021, 5)
    ]
    c.executemany('INSERT OR IGNORE INTO works (title, text, year, poet_id) VALUES (?, ?, ?, ?)', works)

    # Вставка тестовых данных для performances
    performances = [
        (1, 'Любовь и природа', '2023-06-15', 1),
        (2, 'Свобода', '2023-06-15', 2),
        (3, 'Городская лирика', '2022-07-10', 1),
        (4, 'Времена года', '2022-07-10', 2),
        (5, 'Путешествия', '2021-08-20', 1)
    ]
    c.executemany('INSERT OR IGNORE INTO performances (poet_id, theme, date, performance_order) VALUES (?, ?, ?, ?)',
                  performances)

    # Вставка тестовых данных для contests
    contests = [
        (1, 'Январская поэзия', 10),
        (2, 'Зимние мотивы', 12),
        (3, 'Весеннее пробуждение', 15),
        (4, 'Апрельские строки', 18),
        (5, 'Майские стихи', 20),
        (6, 'Летние мечты', 22),
        (7, 'Июльская жара', 25),
        (8, 'Августовский вечер', 14),
        (9, 'Осенние краски', 12),
        (10, 'Октябрьский мотив', 16),
        (11, 'Ноябрьская тишина', 13),
        (12, 'Зимний декабрь', 11)
    ]
    c.executemany('INSERT OR IGNORE INTO contests (month, theme, works_count) VALUES (?, ?, ?)', contests)

    # Вставка тестовых данных для attendance
    attendance = [
        (1, 78, 15),
        (2, 105, 20),
        (3, 115, 25),
        (4, 154, 30),
        (5, 173, 35),
        (6, 221, 40),
        (7, 258, 45),
        (8, 123, 20),
        (9, 95, 18),
        (10, 115, 22),
        (11, 112, 20),
        (12, 109, 18)
    ]
    c.executemany('INSERT OR IGNORE INTO attendance (month, visitors, participants) VALUES (?, ?, ?)', attendance)

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('poetry_contest.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn