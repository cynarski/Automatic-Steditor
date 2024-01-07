# tutaj bedziemy sie laczyc z baza i takie rozne

# todo dodac mozliwosc dodawania rekordow do tabeli

from psycopg2 import connect, OperationalError
from typing import List

# Konfiguracja do polaczenia z nasza baza danych
db_config = {
    'host': 'ep-floral-breeze-43648026.eu-central-1.aws.neon.tech',
    'database': 'AutomaticSteditor',
    'user': 'b.barszczak35@gmail.com',
    'password': 'Cib02anYPEqf',
    'port': '5432',
    'sslmode': 'require'
}


def conncect_to_db():
    """
    Funckja laczy sie z baza danych (PostgreSQL) zapisana w db_config
    :return: polaczenie
    """
    connection = connect(**db_config)

    return connection


def close_connection(connection):
    """
    Funkcja zamyka/konczy polaczenie z baza danych
    :param connection: polaczenie
    :return:
    """
    connection.close()


def dbGetQuery(connection, query: str) -> List:
    """
    Funckja wykonuje zadanie zapytanie
    :param connection: polacznie
    :param query: zapytanie
    :return: lista rekordow
    """
    cursor = connection.cursor()
    cursor.execute(query)

    result = cursor.fetchall()

    cursor.close()

    return result


def dbAddRecord(connection, query: str) -> None:
    cursor = connection.cursor()

    cursor.execute(query)

    cursor.close()
