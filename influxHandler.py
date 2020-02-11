from influxdb import InfluxDBClient

msg1={
        measurement: "comment",
        fields: {
            number:1
        },
        tags:{
            item:msg.payload
        },
}


class influxHandler:
    def __init__(self):
        self.clientIncome = InfluxDBClient("192.168.1.135", 8086, "root", "root", "income")
        self.clientOutcome = InfluxDBClient("192.168.1.135", 8086, "root", "root", "outcome")

    def setup(self):
        self.clientIncome.create_database("income")
        self.clientOutcome.create_database("outcome")

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

    def get_income(self, month):
        cur = self.conn.cursor()
        stmt = "SELECT * FROM income WHERE strftime('%m', date) = '" +month+ "'"
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
        stmt = "SELECT * FROM outcome WHERE strftime('%m', date) = '"+month+"'"
        cur.execute(stmt)
        rows = cur.fetchall()
        return rows

    def get_total_outcome(self, month):
        cur = self.conn.cursor()
        stmt = "SELECT SUM(value) FROM outcome WHERE strftime('%m', date) = '" + month + "'"
        cur.execute(stmt)
        total = cur.fetchone()
        return total[0]