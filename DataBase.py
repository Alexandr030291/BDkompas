import sqlite3
import hashlib
import os


class Database:
    KEYS_DOC = ["обозначение", "наименование", "материал", "форматки"]
    MAX_ID = 1_000_000_000

    def __init__(self, name_db=':memory:'):
        self.conn = sqlite3.connect(name_db)
        self.cur = self.conn.cursor()
        self.__create_table_database()

    def __del__(self):
        self.cur.close()

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
         CREATE TABLE IF NOT EXISTS 'link_item_to_products'(           
                'main' INT,
                'dependent' INT,
                'count' FLOAT,
                CONSTRAINT 'link' PRIMARY KEY ('main', 'dependent')
                );"""
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

    def __get_id_item(self, designation):
        _answer = None
        while _answer is None:
            self.cur.execute("""SELECT 'id' FROM 'items' WHERE 'designation' = ? """, (designation,))
            _answer = self.cur.fetchall()
            if _answer is not None:
                _answer = _answer[0]
            else:
                self.cur.execute("""INSERT INTO 'items' ('designation') VALUES(?) """, (designation,))
                self.conn.commit()
        return _answer

    def add_link_item_to_item(self, main_designation, dependent_designation, count):
        _ids_item = []
        _designations = [main_designation, dependent_designation]
        for _designation in _designations:
            _ids_item.append(self.__get_id_item(_designation))
        self.cur.execute("""SELECT * FROM 'link_item_to_item' WHERE 'main' = ? AND 'dependent' = ? """,
                         (_ids_item[0], _ids_item[1],))
        quest = """UPDATE 'link_item_to_item' SET 'count' = ? WHERE 'main' = ? AND 'dependent' = ? """
        if len(self.cur.fetchall()) == 0:
            quest = """INSERT INTO 'link_item_to_item' ('count', 'main', 'depended') VALUES(?, ?, ?) """
        self.cur.execute(quest, (count, _ids_item[0], _ids_item[1], ))
        self.conn.commit()

    def add_file(self, designation, path):
        self.cur.execute("""SELECT 'id' FROM 'docs' WHERE 'designation' = ? """, (designation,))
        _id_doc = self.cur.fetchall()[0]
        _hash = hashlib.md5(open(path, 'rb').read()).hexdigest()


if __name__ == '__main__':
    name = 'docs_test.db'
    db = Database(name)
    del db
    os.remove(name)
