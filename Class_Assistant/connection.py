import pymysql

def connect():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        port=3306,
        password='system',
        database='class_assistant',
    )
    return conn