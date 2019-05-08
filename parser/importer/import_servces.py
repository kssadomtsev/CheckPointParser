import sys

from database import db_worker
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)


def create_servces():
    conn = db_worker.create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT services FROM security_policy")
        rows = cur.fetchall()
        s = set()
        list = []
        for row in rows:
            print(type(row))
            row_str = str(row).strip("()',")
            print(row_str)
            list.extend(row_str.split(","))
        print(len(list))
        s.update(list)
        print(len(s))
        for s_ in s:
            print(s_)
            cur.execute("SELECT * FROM services WHERE name = '" + s_ + "'")
            rows = cur.fetchall()
            print(rows)
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
