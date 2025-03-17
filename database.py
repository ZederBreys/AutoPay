import sqlite3
import settings


def add_unpaid_user(user_id):
    conn = sqlite3.connect(settings.PATH_DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO payments (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Если пользователь уже существует, игнорируем ошибку
        pass
    finally:
        conn.close()

def get_unpaid_users():
    conn = sqlite3.connect(settings.PATH_DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM payments")
    unpaid_users = cursor.fetchall()
    conn.close()
    return [user[0] for user in unpaid_users]

def remove_unpaid_user(user_id):
    conn = sqlite3.connect(settings.PATH_DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM payments WHERE user_id = ?", (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении пользователя: {e}")
    finally:
        conn.close()

def add_paid_user(user_id, username, date, amount):
    conn = sqlite3.connect(settings.PATH_DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO paid_checks (user_id, username, date, amount) VALUES (?, ?, ?, ?)",
                       (user_id, username, date, amount))
        conn.commit()
    except sqlite3.IntegrityError:
        # Если пользователь уже существует, обновляем запись
        cursor.execute("UPDATE paid_checks SET username=?, date=?, amount=? WHERE user_id=?",
                       (username, date, amount, user_id))
        conn.commit()
    finally:
        conn.close()
