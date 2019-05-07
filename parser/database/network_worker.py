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
    """
    Parser for network objects types: cluster_member, gateway_ckp, connectra, gateway_plain, sofaware_gateway
    :param class_name:
    :param table_name:
    :param root:
    :param conn:
    :return count:
    """
    count = 0
    sql_request = ''' (name,comments,interfaces)
              VALUES(?,?,?) '''
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
            db_worker.create_net_obj(conn, net_obj, table_name, sql_request)
            #            print(net_obj)
            logging.info(net_obj)
            count += 1
    conn.commit()
    return count


def parser_type2(class_name, table_name, root, conn):
    """
    Parser for network objects types: host_plain, host_ckp
    :param class_name:
    :param table_name:
    :param root:
    :param conn:
    :return count:
    """
    count = 0
    sql_request = ''' (name,comments,ip_address)
              VALUES(?,?,?) '''
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text == class_name:
            name = db_worker.del_nt(net_obj_.find('Name').text)
            comment = db_worker.del_nt(net_obj_.find('comments').text)
            logging.info("Now under analyze... " + name)
            ipaddr = db_worker.del_nt(net_obj_.find('ipaddr').text)
            net_obj = (name, comment, ipaddr)
            db_worker.create_net_obj(conn, net_obj, table_name, sql_request)
            #            print(net_obj)
            logging.info(net_obj)
            count += 1
    conn.commit()
    return count


def parser_type3(class_name, table_name, root, conn):
    """
    Parser for network objects types: address_range
    :param class_name:
    :param table_name:
    :param root:
    :param conn:
    :return count:
    """
    count = 0
    sql_request = ''' (name,comments,ipaddr_first,ipaddr_last)
              VALUES(?,?,?,?) '''
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text == class_name:
            name = db_worker.del_nt(net_obj_.find('Name').text)
            comment = db_worker.del_nt(net_obj_.find('comments').text)
            logging.info("Now under analyze... " + name)
            ipaddr_first = db_worker.del_nt(net_obj_.find('ipaddr_first').text)
            ipaddr_last = db_worker.del_nt(net_obj_.find('ipaddr_last').text)
            net_obj = (name, comment, ipaddr_first, ipaddr_last)
            db_worker.create_net_obj(conn, net_obj, table_name, sql_request)
            #            print(net_obj)
            logging.info(net_obj)
            count += 1
    conn.commit()
    return count


def parser_type4(class_name, table_name, root, conn):
    """
    Parser for network objects types: network
    :param class_name:
    :param table_name:
    :param root:
    :param conn:
    :return count:
    """
    count = 0
    sql_request = ''' (name,comments,ip_address)
              VALUES(?,?,?) '''
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text == class_name:
            name = db_worker.del_nt(net_obj_.find('Name').text)
            comment = db_worker.del_nt(net_obj_.find('comments').text)
            logging.info("Now under analyze... " + name)
            ip_addr = db_worker.del_nt(net_obj_.find('ipaddr').text)
            netmask = db_worker.del_nt(net_obj_.find('netmask').text)
            net_obj = (name, comment, ip_addr + '/' + netmask)
            db_worker.create_net_obj(conn, net_obj, table_name, sql_request)
            #            print(net_obj)
            logging.info(net_obj)
            count += 1
    conn.commit()
    return count


def parser_type5(class_name, table_name, root, conn):
    """
    Parser for network objects types: gateway_cluster
    :param class_name:
    :param table_name:
    :param root:
    :param conn:
    :return count:
    """
    count = 0
    sql_request = ''' (name,comments,nodes)
              VALUES(?,?,?) '''
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text == class_name:
            name = db_worker.del_nt(net_obj_.find('Name').text)
            comment = db_worker.del_nt(net_obj_.find('comments').text)
            logging.info("Now under analyze... " + name)
            nodes = []
            for cluster_members in net_obj_.findall('cluster_members'):
                cluster_members_ = cluster_members.findall('cluster_members')
                for cluster_member_ in cluster_members_:
                    nodes.append(db_worker.del_nt(cluster_member_.find('Name').text))
            nodes_str = " , ".join(nodes)
            net_obj = (name, comment, nodes_str)
            db_worker.create_net_obj(conn, net_obj, table_name, sql_request)
            #            print(net_obj)
            logging.info(net_obj)
            count += 1
    conn.commit()
    return count


def parser_type6(class_name, table_name, root, conn):
    """
    Parser for network objects types: network_object_group
    :param class_name:
    :param table_name:
    :param root:
    :param conn:
    :return count:
    """
    count = 0
    sql_request = ''' (name,comments,members)
              VALUES(?,?,?) '''
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text == class_name:
            name = db_worker.del_nt(net_obj_.find('Name').text)
            comment = db_worker.del_nt(net_obj_.find('comments').text)
            logging.info("Now under analyze... " + name)
            members = []
            for group_member in net_obj_.findall('members'):
                elements = group_member.findall('reference')
                for element in elements:
                    members.append(db_worker.del_nt(element.find('Name').text))
            members_str = " , ".join(members)
            net_obj = (name, comment, members_str)
            db_worker.create_net_obj(conn, net_obj, table_name, sql_request)
            logging.info(net_obj)
            count += 1
    conn.commit()
    return count


def parser_type7(class_name, table_name, root, conn):
    """
    Parser for network objects types: group_with_exception
    :param class_name:
    :param table_name:
    :param root:
    :param conn:
    :return count:
    """
    count = 0
    sql_request = ''' (name,comments,members,exceptions)
              VALUES(?,?,?,?) '''
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text == class_name:
            name = db_worker.del_nt(net_obj_.find('Name').text)
            comment = db_worker.del_nt(net_obj_.find('comments').text)
            logging.info("Now under analyze... " + name)
            members = []
            exceptions = []
            for obj in net_obj_.findall('base'):
                members.append(db_worker.del_nt(obj.find('Name').text))
            for obj in net_obj_.findall('exception'):
                exceptions.append(db_worker.del_nt(obj.find('Name').text))
            members_str = " , ".join(members)
            exceptions_str = " , ".join(exceptions)
            net_obj = (name, comment, members_str, exceptions_str)
            db_worker.create_net_obj(conn, net_obj, table_name, sql_request)
            logging.info(net_obj)
            count += 1
    conn.commit()
    return count


def parse_list_network_object(filename, conn):
    f = open(filename, 'rU')
    type_net_obj = []
    tree = ET.parse(filename, ET.XMLParser(encoding="cp1251"))
    root = tree.getroot()
    print(root)

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
    count_sofaware_gateway = parser_type1('sofaware_gateway', 'sofaware_gateway', root, conn)
    count_host_plain = parser_type2('host_plain', 'host_plain', root, conn)
    count_host_ckp = parser_type2('host_ckp', 'host_ckp', root, conn)
    count_address_range = parser_type3('address_range', 'address_range', root, conn)
    count_network = parser_type4('network', 'network', root, conn)
    count_gateway_cluster = parser_type5('gateway_cluster', 'gateway_cluster', root, conn)
    j = 0
    # At first let's count how many network_object_group we have
    for net_obj_ in root.findall('network_object'):
        if net_obj_.find('Class_Name').text == 'network_object_group':
            j += 1
    print("Count of network_object_group is... " + str(j))
    logging.info("Count of network_object_group is... " + str(j))

    count_network_group = parser_type6('network_object_group', 'network_object_group', root, conn)
    count_group_with_exception = parser_type7('group_with_exception', 'group_with_exception', root, conn)

    print('**********************************************************************')
    print('Numbers of cluster_member = ' + str(count_cluster_member))
    print('Numbers of gateway_ckp = ' + str(count_gateway_ckp))
    print('Numbers of connectra = ' + str(count_connectra))
    print('Numbers of gateway_plain = ' + str(count_gateway_plain))
    print('Numbers of sofaware_gateway = ' + str(count_sofaware_gateway))
    print('Numbers of host_plain = ' + str(count_host_plain))
    print('Numbers of host_ckp = ' + str(count_host_ckp))
    print('Numbers of address_range = ' + str(count_address_range))
    print('Numbers of network = ' + str(count_network))
    print('Numbers of gateway_cluster = ' + str(count_gateway_cluster))
    print('Numbers of network_group = ' + str(count_network_group))
    print('Numbers of group_with_exception = ' + str(count_group_with_exception))

    logging.info('**********************************************************************')
    logging.info('Numbers of cluster_member = ' + str(count_cluster_member))
    logging.info('Numbers of gateway_ckp = ' + str(count_gateway_ckp))
    logging.info('Numbers of connectra = ' + str(count_connectra))
    logging.info('Numbers of gateway_plain = ' + str(count_gateway_plain))
    logging.info('Numbers of sofaware_gateway = ' + str(count_sofaware_gateway))
    logging.info('Numbers of host_plain = ' + str(count_host_plain))
    logging.info('Numbers of host_ckp = ' + str(count_host_ckp))
    logging.info('Numbers of address_range = ' + str(count_address_range))
    logging.info('Numbers of network = ' + str(count_network))
    logging.info('Numbers of gateway_cluster = ' + str(count_gateway_cluster))
    logging.info('Numbers of network_group = ' + str(count_network_group))
    logging.info('Numbers of group_with_exception = ' + str(count_group_with_exception))

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
                                         ipaddr_first text,
                                         ipaddr_last text
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
