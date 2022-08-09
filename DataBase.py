import sqlite3
import hashlib


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
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'designation' TEXT ,
                'name' TEXT,
                'A0' INT, 'A1' INT, 'A2' INT, 'A3' INT, 'A4' INT, 'A5' INT,
                'file' INT,
                UNIQUE ('designation')
            );
        """, """
            CREATE TABLE IF NOT EXISTS 'files'(           
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'path' TEXT,
                'hash' TEXT,
                UNIQUE ('path')
                );
         """, """
            CREATE TABLE IF NOT EXISTS 'items'(           
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'designation' TEXT NOT NULL,
                'name' TEXT NOT NULL,
                'billet' INT DEFAULT 0,
                'billet_type' INT DEFAULT 0,
                UNIQUE ('designation')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'materials'(           
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'name' TEXT,
                UNIQUE ('name')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'products'(           
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'name' TEXT,
                'type' CHAR,
                UNIQUE ('name')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'link_item_to_item'(           
                'main' INT ,
                'dependent' INT ,
                'count' FLOAT,
                CONSTRAINT 'link' PRIMARY KEY ('main', 'dependent')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'link_item_to_docs'(           
                'main' INT ,
                'dependent' INT ,
                CONSTRAINT 'link' PRIMARY KEY ('main', 'dependent')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'link_item_to_materials'(           
                'main' INT,
                'dependent' INT,
                'count' FLOAT,
                CONSTRAINT 'link' PRIMARY KEY ('main', 'dependent')
                );
         """, """
         CREATE TABLE IF NOT EXISTS 'link_item_to_materials'(           
                'main' INT,
                'dependent' INT,
                'count' FLOAT,
                CONSTRAINT 'link' PRIMARY KEY ('main', 'products')
                );
         """
                    ]
        self.cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='billet_type'""")
        if len(self.cur.fetchall()) == 0:
            commands += ["""
                     CREATE TABLE 'billet_type'(           
                            'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                            'name' TEXT,
                            UNIQUE ('name')
                            );
                     """, """
                     INSERT INTO 'billet_type' ('id', 'name') VALUES(0, 'Нет');
                     """, """
                     INSERT INTO 'billet_type' ('id', 'name') VALUES(1, 'Материал');
                     """, """
                     INSERT INTO 'billet_type' ('id', 'name') VALUES(2, 'Собственное изделие');
                     """, """
                     INSERT INTO 'billet_type' ('id', 'name') VALUES(3, 'Покупное изделие');
                     """
                         ]
        for command in commands:
            self.cur.execute(command)
            self.conn.commit()


if __name__ == '__main__':
    db = Database(
        'docs.db'
    )
