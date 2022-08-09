import sqlite3


class Database:
    KEYS_DOC = ["обозначение", "наименование", "материал", "формаки"]
    MAX_ID = 1_000_000_000

    def __init__(self, fname):
        self.conn = sqlite3.connect(fname)
        self.cur = self.conn.cursor()
        self.__create_table_doc()

    def __create_table_doc(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS docs(           
           id INT PRIMARY KEY,
           designation TEXT ,
           name TEXT,
           A0 INT, A1 INT, A2 INT, A3 INT, A4 INT, A5 INT,
           UNIQUE (designation)
           );
        """)
        self.conn.commit()


if __name__ == '__main__':
    db = Database('docs.db')