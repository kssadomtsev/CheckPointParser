import sys
from database import db_worker
from model import network_objects
from importer import api_worker
import logging
import ipaddress

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)

list_network_objects = []


def create_host_plain(host_plain, cur):
    cur.execute("SELECT * FROM host_plain WHERE name='%s'" % (host_plain,))
    rows = cur.fetchone()
    host_plain_obj = network_objects.host_plain(db_worker.del_g_host(rows[0]), rows[1], rows[2].lower(), rows[3])
    logging.info("Trying to add to SMS host_plain " + host_plain_obj.name)
    api_worker.create_object("add-host", {"name": host_plain_obj.name, "comments": host_plain_obj.comments,
                                          "ip-address": host_plain_obj.ip_address,
                                          "color": api_worker.choose_color(host_plain_obj),
                                          "ignore-warnings": "true"})


def create_network(network, cur):
    cur.execute("SELECT * FROM network WHERE name='%s'" % (network,))
    rows = cur.fetchone()
    network_obj = network_objects.host_plain(db_worker.del_g_net(rows[0]), rows[1], rows[2].lower(), rows[3])
    logging.info("Trying to add to SMS network " + network_obj.name + " " + network_obj.ip_address)
    ip = ipaddress.ip_network(network_obj.ip_address)
    api_worker.create_object("add-network", {"name": network_obj.name, "comments": network_obj.comments,
                                             "subnet": str(ip.network_address),
                                             "mask-length": str(ip.prefixlen),
                                             "color": api_worker.choose_color(network_obj),
                                             "ignore-warnings": "true"})


def create_address_range(address_range, cur):
    cur.execute("SELECT * FROM address_range WHERE name='%s'" % (address_range,))
    rows = cur.fetchone()
    address_range_obj = network_objects.address_range(rows[0], rows[1], rows[2].lower(), rows[3], rows[4])
    logging.info("Trying to add to SMS address_range " + address_range_obj.name)
    api_worker.create_object("add-address-range",
                             {"name": address_range_obj.name, "comments": address_range_obj.comments,
                              "ip-address-first": address_range_obj.ipaddr_first,
                              "ip-address-last": address_range_obj.ipaddr_last,
                              "color": api_worker.choose_color(address_range_obj),
                              "ignore-warnings": "true"})


def create_network_objects():
    conn = db_worker.create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT src FROM security_policy")
        rows1 = cur.fetchall()
        cur.execute("SELECT DISTINCT dst FROM security_policy")
        rows2 = cur.fetchall()
        rows = rows1 + rows2
        s = set()
        list = []
        for row in rows:
            row_str = str(row).strip("()',")
            list.extend(row_str.split(","))
        logging.info("Total number of network objects in rules " + str(len(list)))
        s.update(list)
        logging.info("Total number of unique network objects  in rules " + str(len(s)))
        logging.info("Those network objects  are " + str(s))
        for s_ in s:
            cur.execute("SELECT type FROM network_object_index WHERE name =(?)", (s_,))
            rows = cur.fetchone()
            if rows != None:
                row_str_ = str(rows).strip("()',")
                if row_str_ == "host_plain" and db_worker.del_g_host(s_) not in list_network_objects:
                    s2_ = db_worker.del_g_host(s_)
                    list_network_objects.append(s2_)
                    logging.info("Creating host_plain " + s2_)
                    create_host_plain(s_, cur)
                elif row_str_ == "network" and db_worker.del_g_net(s_) not in list_network_objects:
                    s2_ = db_worker.del_g_net(s_)
                    list_network_objects.append(s2_)
                    logging.info("Creating network " + s2_)
                    create_network(s_, cur)
                elif row_str_ == "address_range" and s_ not in list_network_objects:
                    list_network_objects.append(s_)
                    logging.info("Creating address_range " + s_)
                    create_address_range(s_, cur)
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
