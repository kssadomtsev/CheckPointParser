from sqlite3 import Error
from database import db_worker
import xml.etree.ElementTree as ET
import re

import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)


# Checking than string contains
def is_ip_addr(ip_addr_str):
    if ip_addr_str:
        match = re.search(r"^.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*", ip_addr_str)
        return match
    return None


def parser_type1(class_name, table_name, root, conn):
    count = 0
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text == class_name:
            name = db_worker.del_nt(net_obj_.find('Name').text)
            comment = db_worker.del_nt(net_obj_.find('comments').text)
            logging.info("Now under analyze... " + name)
            interfaces = []
            for interface in net_obj_.findall('interfaces'):
                interfaces_ = interface.findall('interfaces')
                for interface_ in interfaces_:
                    ip = db_worker.del_nt(interface_.find('ipaddr').text)
                    if is_ip_addr(ip):
                        interfaces.append(ip)
            ipaddr = db_worker.del_nt(interface_.find('ipaddr').text)
            if ipaddr not in interfaces and ipaddr is not None:
                interfaces.append(ipaddr)
            interfaces_str = " , ".join(interfaces)
            net_obj = (name, comment, interfaces_str)
            count += 1
            print(net_obj)
            logging.info(net_obj)
    return count


def parse_list_network_object(filename, conn):
    f = open(filename, 'rU')
    type_net_obj = []
    tree = ET.parse(filename, ET.XMLParser(encoding="cp1251"))
    root = tree.getroot()
    print(root)
    count_host_plain = 0
    count_host_ckp = 0
    count_address_range = 0
    count_network = 0
    count_sofaware_gateway = 0
    count_gateway_cluster = 0
    count_network_group = 0
    count_group_with_exception = 0
    # Determine how many network object types we have
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text not in type_net_obj:
            type_net_obj.append(net_obj_.find('Class_Name').text)
    # Print all network object types
    print("***************** We have following network object types:***********************")
    logging.info("***************** We have following network object types:***********************")
    for net_obj_type_ in type_net_obj:
        print(net_obj_type_)
        logging.info(net_obj_type_)
    count_cluster_member = parser_type1('cluster_member', 'cluster_member', root, conn)
    count_gateway_ckp = parser_type1('gateway_ckp', 'gateway_ckp', root, conn)
    count_connectra = parser_type1('connectra', 'connectra', root, conn)
    count_gateway_plain = parser_type1('gateway_plain', 'gateway_plain', root, conn)
    f.close()


def create_list_network_object(filepath):
    sql_create_cluster_member_table = """ CREATE TABLE IF NOT EXISTS cluster_member (
                                         name text PRIMARY KEY,
                                         comments text,
                                         interfaces text
                                     ); """
    sql_create_connectra_table = """ CREATE TABLE IF NOT EXISTS connectra (
                                         name text PRIMARY KEY,
                                         comments text,
                                         interfaces text
                                     ); """
    sql_create_gateway_ckp_table = """ CREATE TABLE IF NOT EXISTS gateway_ckp (
                                         name text PRIMARY KEY,
                                         comments text,
                                         interfaces text
                                     ); """
    sql_create_gateway_plain_table = """ CREATE TABLE IF NOT EXISTS gateway_plain (
                                         name text PRIMARY KEY,
                                         comments text,
                                         interfaces text
                                     ); """
    sql_create_sofaware_gateway_table = """ CREATE TABLE IF NOT EXISTS sofaware_gateway (
                                         name text PRIMARY KEY,
                                         comments text,
                                         interfaces text
                                     ); """
    sql_create_gateway_cluster_table = """ CREATE TABLE IF NOT EXISTS gateway_cluster (
                                         name text PRIMARY KEY,
                                         comments text,
                                         nodes text
                                     ); """
    sql_create_address_range_table = """ CREATE TABLE IF NOT EXISTS address_range (
                                         name text PRIMARY KEY,
                                         comments text,
                                         ip_addresses text
                                     ); """
    sql_create_host_plain_table = """ CREATE TABLE IF NOT EXISTS host_plain (
                                         name text PRIMARY KEY,
                                         comments text,
                                         ip_address text
                                     ); """
    sql_create_host_ckp_table = """ CREATE TABLE IF NOT EXISTS host_ckp (
                                         name text PRIMARY KEY,
                                         comments text,
                                         ip_address text
                                     ); """
    sql_create_network_table = """ CREATE TABLE IF NOT EXISTS network (
                                         name text PRIMARY KEY,
                                         comments text,
                                         ip_address text
                                     ); """
    sql_create_group_with_exception_table = """ CREATE TABLE IF NOT EXISTS group_with_exception (
                                         name text PRIMARY KEY,
                                         comments text,
                                         members text,
                                         exceptions text
                                     ); """
    sql_create_network_object_group_table = """ CREATE TABLE IF NOT EXISTS network_object_group (
                                         name text PRIMARY KEY,
                                         comments text,
                                         members text
                                     ); """

    conn = db_worker.create_connection()
    if conn is not None:
        db_worker.create_table(conn, sql_create_cluster_member_table)
        db_worker.create_table(conn, sql_create_connectra_table)
        db_worker.create_table(conn, sql_create_gateway_ckp_table)
        db_worker.create_table(conn, sql_create_gateway_plain_table)
        db_worker.create_table(conn, sql_create_sofaware_gateway_table)
        db_worker.create_table(conn, sql_create_gateway_cluster_table)
        db_worker.create_table(conn, sql_create_address_range_table)
        db_worker.create_table(conn, sql_create_host_plain_table)
        db_worker.create_table(conn, sql_create_host_ckp_table)
        db_worker.create_table(conn, sql_create_network_table)
        db_worker.create_table(conn, sql_create_group_with_exception_table)
        db_worker.create_table(conn, sql_create_network_object_group_table)
        parse_list_network_object(filepath + "\\network_objects_new.xml", conn)
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
