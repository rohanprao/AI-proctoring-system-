import sqlite3
from werkzeug.security import check_password_hash

conn = sqlite3.connect('users.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('SELECT * FROM users WHERE username = ?', ('testuser',))
user = cursor.fetchone()
conn.close()

if user:
    print(f"User found: {user['username']}")
    print(f"Stored hash: {user['password']}")
    password = "password123"
    result = check_password_hash(user['password'], password)
    print(f"Check result for '{password}': {result}")
else:
    print("User not found")
