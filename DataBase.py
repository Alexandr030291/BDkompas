import sqlite3


class Database:
    KEYS_DOC = ["обозначение", "наименование", "материал", "форматки"]
    MAX_ID = 1_000_000_000

    def __init__(self, name=':memory:'):
        self.conn = sqlite3.connect(name)
        self.cur = self.conn.cursor()
        self.__create_table_database()

    def __create_table_database(self):
        commands = ["""
            CREATE TABLE IF NOT EXISTS 'docs'(           
                'id' INT PRIMARY KEY,
                'designation' TEXT ,
                'name' TEXT,
                'A0' INT, 'A1' INT, 'A2' INT, 'A3' INT, 'A4' INT, 'A5' INT,
                UNIQUE ('designation')
            );
        """, """
            CREATE TABLE IF NOT EXISTS 'items'(           
                'id' INT PRIMARY KEY,
                'designation' TEXT ,
                'name' TEXT,
                'billet' INT,
                'billet_type' INT,
                UNIQUE ('designation')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'materials'(           
                'id' INT PRIMARY KEY,
                'name' TEXT,
                UNIQUE ('name')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'billet_type'(           
                'id' INT PRIMARY KEY,
                'name' TEXT,
                UNIQUE ('name')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'products'(           
                'id' INT PRIMARY KEY,
                'name' TEXT,
                UNIQUE ('name')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'products'(           
                'id' INT PRIMARY KEY,
                'name' TEXT,
                UNIQUE ('name')
                );
         """]
        for command in commands:
            self.cur.execute(command)
            self.conn.commit()


if __name__ == '__main__':
    db = Database(
        'docs.db'
    )
