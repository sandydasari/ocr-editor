import sqlite3
from enum import Enum
conn = sqlite3.connect("books.sqlite")

cursor = conn.cursor()
sql_query = """
            CREATE TABLE book (
                bookuuid BLOB PRIMARY KEY NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                fullpath TEXT NOT NULL,
                noofpages INTEGER NOT NULL,
                isIndexed INTEGER NOT NULL DEFAULT '0',
                category TEXT NOT NULL
            );
        """
cursor.execute(sql_query)
