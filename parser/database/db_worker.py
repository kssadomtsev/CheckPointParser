import sqlite3
from sqlite3 import Error
from pathlib import Path
import re
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)


# Function for delete \t\n
def del_nt(str):
    if str:
        return re.sub('[\t\n]', '', str)
    return str


# Function for delete CDATA
def del_CDATA(string_CDATA):
    match = re.search(r"^\s*?([^\s].*)\s*$", string_CDATA, flags=re.UNICODE)
    if match:
        result = match.group(1)
    else:
        result = " "
    return result


def create_connection():
    """ create a database connection to a SQLite database """
    p = Path(__file__).parents[2]
    try:
        conn = sqlite3.connect(str(p) + "\\data\\pythonsqlite.db")
        print(sqlite3.version)
        return conn
    except Error as e:
        logging.warning(e)
    return None


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        logging.warning(e)
