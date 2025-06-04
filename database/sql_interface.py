import mysql.connector
from config.config import DB_CONFIG

def get_all_boxes():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT commonId, length, width, height, shape FROM Objects")
        result = cursor.fetchall()

        cursor.close()
        conn.close()
        return result

    except mysql.connector.Error as e:
        print(f"[SQL ERROR] {e}")
        return []
