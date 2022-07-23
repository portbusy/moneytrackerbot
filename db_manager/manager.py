import sqlite3
import typing


class DatabaseManager:
    def __init__(self, dbname="expenses.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        outcome = "CREATE TABLE IF NOT EXISTS outcome (date date, value float, comment varchar(50))"
        income = "CREATE TABLE IF NOT EXISTS income (date date, value float, comment varchar(50))"
        self.conn.execute(outcome)
        self.conn.execute(income)
        self.conn.commit()

    def add_income(self, date, value, comment):
        stmt = "INSERT INTO income (date, value, comment) VALUES (?, ?, ?)"
        args = (date, value, comment)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def add_outcome(self, date, value, comment):
        stmt = "INSERT INTO outcome (date, value, comment) VALUES (?, ?, ?)"
        args = (date, value, comment)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_income(self, value, comment):
        stmt = "DELETE FROM income WHERE value = (?) AND comment = (?)"
        args = (value, comment)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_outcome(self, value, comment):
        stmt = "DELETE FROM outcome WHERE value = (?) AND comment = (?)"
        args = (value, comment)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_income(self, month) -> typing.List:
        cur = self.conn.cursor()
        stmt = "SELECT * FROM income WHERE strftime('%m', date) = '" + month + "'"
        cur.execute(stmt)
        rows = cur.fetchall()
        return rows

    def get_total_income(self, month):
        cur = self.conn.cursor()
        stmt = "SELECT SUM(value) FROM income WHERE strftime('%m', date) = '" + month + "'"
        cur.execute(stmt)
        total = cur.fetchone()
        return total[0]

    def get_outcome(self, month):
        cur = self.conn.cursor()
        stmt = "SELECT * FROM outcome WHERE strftime('%m', date) = '" + month + "'"
        cur.execute(stmt)
        rows = cur.fetchall()
        return rows

    def get_total_outcome(self, month):
        cur = self.conn.cursor()
        stmt = "SELECT SUM(value) FROM outcome WHERE strftime('%m', date) = '" + month + "'"
        cur.execute(stmt)
        total = cur.fetchone()
        return total[0]
