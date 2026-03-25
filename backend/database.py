import pymysql
import bcrypt
from datetime import datetime
import json

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'xiaoshuo',
    'charset': 'utf8mb4'
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            title VARCHAR(100) NOT NULL,
            style VARCHAR(50) NOT NULL,
            date VARCHAR(20),
            cover_url VARCHAR(255) DEFAULT NULL,
            description TEXT DEFAULT NULL,
            word_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_id (user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INT PRIMARY KEY AUTO_INCREMENT,
            book_id INT NOT NULL,
            user_id INT NOT NULL,
            title VARCHAR(200) DEFAULT '',
            content LONGTEXT,
            word_count INT DEFAULT 0,
            sort_order INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_book_id (book_id),
            INDEX idx_user_id (user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_settings (
            id INT PRIMARY KEY AUTO_INCREMENT,
            book_id INT NOT NULL UNIQUE,
            user_id INT NOT NULL,
            world_setting TEXT,
            outline TEXT,
            character_setting TEXT,
            inspiration TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_book_id (book_id)
        )
    ''')

    conn.commit()
    conn.close()
    print('数据库初始化完成')

def create_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (%s, %s)',
            (username, hashed.decode('utf-8'))
        )
        conn.commit()
        conn.close()
        return True
    except pymysql.IntegrityError:
        conn.close()
        return False

def verify_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        return {'id': user[0], 'username': user[1]}
    return None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, created_at FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'id': user[0], 'username': user[1], 'created_at': user[2]}
    return None

def get_books_by_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.title, b.style, b.date, b.word_count, b.description,
               (SELECT COUNT(*) FROM chapters c WHERE c.book_id = b.id) as chapter_count
        FROM books b
        WHERE b.user_id = %s
        ORDER BY b.created_at DESC
    ''', (user_id,))
    books = cursor.fetchall()
    conn.close()

    result = []
    for book in books:
        result.append({
            'id': book[0],
            'title': book[1],
            'style': book[2],
            'date': book[3],
            'word_count': book[4] or 0,
            'description': book[5] or '',
            'chapter_count': book[6] or 0
        })
    return result

def create_book(user_id, title, style, description=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO books (user_id, title, style, date, description) VALUES (%s, %s, %s, %s, %s)',
        (user_id, title, style, datetime.now().strftime('%Y-%m-%d'), description)
    )
    book_id = cursor.lastrowid

    cursor.execute(
        'INSERT INTO book_settings (book_id, user_id) VALUES (%s, %s)',
        (book_id, user_id)
    )

    conn.commit()
    conn.close()
    return book_id

def update_book(book_id, user_id, title, style, description=None):
    conn = get_db()
    cursor = conn.cursor()

    if description is not None:
        cursor.execute(
            'UPDATE books SET title = %s, style = %s, description = %s WHERE id = %s AND user_id = %s',
            (title, style, description, book_id, user_id)
        )
    else:
        cursor.execute(
            'UPDATE books SET title = %s, style = %s WHERE id = %s AND user_id = %s',
            (title, style, book_id, user_id)
        )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def delete_book(book_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chapters WHERE book_id = %s AND user_id = %s', (book_id, user_id))
    cursor.execute('DELETE FROM book_settings WHERE book_id = %s AND user_id = %s', (book_id, user_id))
    cursor.execute('DELETE FROM books WHERE id = %s AND user_id = %s', (book_id, user_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def get_book_by_id(book_id, user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, style, date, description, word_count
        FROM books WHERE id = %s AND user_id = %s
    ''', (book_id, user_id))
    book = cursor.fetchone()

    if not book:
        conn.close()
        return None

    cursor.execute('''
        SELECT id, title, content, word_count, sort_order
        FROM chapters WHERE book_id = %s AND user_id = %s
        ORDER BY sort_order, id
    ''', (book_id, user_id))
    chapters = cursor.fetchall()

    cursor.execute('''
        SELECT world_setting, outline, character_setting, inspiration
        FROM book_settings WHERE book_id = %s AND user_id = %s
    ''', (book_id, user_id))
    settings_row = cursor.fetchone()

    conn.close()

    chapters_list = []
    for c in chapters:
        chapters_list.append({
            'id': c[0],
            'title': c[1] or '',
            'content': c[2] or '',
            'words': c[3] or 0,
            'order': c[4]
        })

    settings = {
        'world': settings_row[0] or '' if settings_row else '',
        'outline': settings_row[1] or '' if settings_row else '',
        'character': settings_row[2] or '' if settings_row else '',
        'inspiration': settings_row[3] or '' if settings_row else ''
    }

    return {
        'id': book[0],
        'title': book[1],
        'style': book[2],
        'date': book[3],
        'description': book[4] or '',
        'word_count': book[5] or 0,
        'chapters': chapters_list,
        'settings': settings
    }

def add_chapter(book_id, user_id, title='', content=''):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM chapters WHERE book_id = %s AND user_id = %s ORDER BY sort_order DESC LIMIT 1', (book_id, user_id))
    last = cursor.fetchone()
    new_order = (last[0] + 1) if last else 0

    cursor.execute('''
        INSERT INTO chapters (book_id, user_id, title, content, word_count, sort_order)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (book_id, user_id, title, content, len(content), new_order))

    chapter_id = cursor.lastrowid

    update_book_word_count(book_id, user_id, cursor)
    conn.commit()
    conn.close()
    return chapter_id

def update_chapter(chapter_id, user_id, title=None, content=None):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT book_id FROM chapters WHERE id = %s AND user_id = %s', (chapter_id, user_id))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False

    book_id = result[0]

    if title is not None:
        cursor.execute('UPDATE chapters SET title = %s WHERE id = %s AND user_id = %s', (title, chapter_id, user_id))
    if content is not None:
        cursor.execute('UPDATE chapters SET content = %s, word_count = %s WHERE id = %s AND user_id = %s',
                       (content, len(content), chapter_id, user_id))

    update_book_word_count(book_id, user_id, cursor)
    conn.commit()
    conn.close()
    return True

def delete_chapter(chapter_id, user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT book_id FROM chapters WHERE id = %s AND user_id = %s', (chapter_id, user_id))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False

    book_id = result[0]

    cursor.execute('DELETE FROM chapters WHERE id = %s AND user_id = %s', (chapter_id, user_id))
    update_book_word_count(book_id, user_id, cursor)
    conn.commit()
    conn.close()
    return True

def update_book_word_count(book_id, user_id, cursor):
    cursor.execute('SELECT SUM(word_count) FROM chapters WHERE book_id = %s AND user_id = %s', (book_id, user_id))
    result = cursor.fetchone()
    total = result[0] or 0
    cursor.execute('UPDATE books SET word_count = %s WHERE id = %s', (total, book_id))

def update_book_settings(book_id, user_id, settings):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE book_settings
        SET world_setting = %s, outline = %s, character_setting = %s, inspiration = %s
        WHERE book_id = %s AND user_id = %s
    ''', (
        settings.get('world', ''),
        settings.get('outline', ''),
        settings.get('character', ''),
        settings.get('inspiration', ''),
        book_id, user_id
    ))

    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def reorder_chapters(book_id, user_id, chapter_orders):
    conn = get_db()
    cursor = conn.cursor()

    for i, chapter_id in enumerate(chapter_orders):
        cursor.execute(
            'UPDATE chapters SET sort_order = %s WHERE id = %s AND book_id = %s AND user_id = %s',
            (i, chapter_id, book_id, user_id)
        )

    conn.commit()
    conn.close()
    return True

if __name__ == '__main__':
    init_db()
    print('数据库初始化完成')
