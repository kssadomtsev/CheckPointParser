from database import db_worker
import xml.etree.ElementTree as ET
import re
from sqlite3 import Error
from importer import output

import logging

logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename="..\\logs\\parser_log.log",
                    level=logging.DEBUG, filemode='w')
logging._defaultFormatter = logging.Formatter(r"%(message)s")
groups_list = {}


# Checking than string contains
def is_ip_addr(ip_addr_str):
    if ip_addr_str:
        match = re.search(r"^.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*", ip_addr_str)
        return match
    return None


def parser_type1(net_obj_):
    """
    Parser for network objects types: cluster_member, gateway_ckp, connectra, gateway_plain, sofaware_gateway
    :param net_obj_:
    :return net_obj_tail:
    """

    interfaces = []
    for interface in net_obj_.findall('interfaces'):
        interfaces_ = interface.findall('interfaces')
        for interface_ in interfaces_:
            ip = db_worker.del_nt(interface_.find('ipaddr').text)
            if is_ip_addr(ip):
                interfaces.append(ip)
    ipaddr = db_worker.del_nt(net_obj_.find('ipaddr').text)
    if ipaddr not in interfaces and ipaddr is not None:
        interfaces.append(ipaddr)
    interfaces_str = ",".join(interfaces)
    return (interfaces_str,)


def parser_type2(net_obj_):
    """
    Parser for network objects types: host_plain, host_ckp
    :param net_obj_:
    :return net_obj_tail:
    """

    ipaddr = db_worker.del_nt(net_obj_.find('ipaddr').text)
    return (ipaddr,)


def parser_type3(net_obj_):
    """
    Parser for network objects types: address_range
    :param net_obj_:
    :return net_obj_tail:
    """

    ipaddr_first = db_worker.del_nt(net_obj_.find('ipaddr_first').text)
    ipaddr_last = db_worker.del_nt(net_obj_.find('ipaddr_last').text)
    return (ipaddr_first, ipaddr_last)


def parser_type4(net_obj_):
    """
    Parser for network objects types: network
    :param net_obj_:
    :return net_obj_tail:
    """

    ip_addr = db_worker.del_nt(net_obj_.find('ipaddr').text)
    netmask = db_worker.del_nt(net_obj_.find('netmask').text)
    return (ip_addr + '/' + netmask,)


def parser_type5(net_obj_):
    """
    Parser for network objects types: gateway_cluster
    :param net_obj_:
    :return net_obj_tail:
    """

    nodes = []
    for cluster_members in net_obj_.findall('cluster_members'):
        cluster_members_ = cluster_members.findall('cluster_members')
        for cluster_member_ in cluster_members_:
            nodes.append(db_worker.del_nt(cluster_member_.find('Name').text))
    nodes_str = ",".join(nodes)
    return (nodes_str,)


def parser_type6(net_obj_):
    """
    Parser for network objects types: network_object_group
    :param net_obj_:
    :return net_obj_tail:
    """

    members = []
    for group_member in net_obj_.findall('members'):
        elements = group_member.findall('reference')
        for element in elements:
            members.append(db_worker.del_nt(element.find('Name').text))
    members_str = ",".join(members)
    return (members_str,)


def parser_type7(net_obj_):
    """
    Parser for network objects types: group_with_exception
    :param net_obj_:
    :return net_obj_tail:
    """

    members = []
    exceptions = []
    for obj in net_obj_.findall('base'):
        members.append(db_worker.del_nt(obj.find('Name').text))
    for obj in net_obj_.findall('exception'):
        exceptions.append(db_worker.del_nt(obj.find('Name').text))
    members_str = ",".join(members)
    exceptions_str = ",".join(exceptions)
    return (members_str, exceptions_str)


def parse_list_network_object(filename, conn):
    f = open(filename, 'rU')
    type_net_obj = []
    tree = ET.parse(filename)
    root = tree.getroot()
    print(root)
    net_obj_type_dict = {
        'cluster_member': ''' (name,comments,color,interfaces)
              VALUES(?,?,?,?) ''',
        'gateway_ckp': ''' (name,comments,color,interfaces)
              VALUES(?,?,?,?) ''',
        'gateway_plain': ''' (name,comments,color,interfaces)
              VALUES(?,?,?,?) ''',
        'sofaware_gateway': ''' (name,comments,color,interfaces)
              VALUES(?,?,?,?) ''',
        'connectra': ''' (name,comments,color,interfaces)
          VALUES(?,?,?,?) ''',
        'host_plain': ''' (name,comments,color,ip_address)
              VALUES(?,?,?,?) ''',
        'host_ckp': ''' (name,comments,color,ip_address)
              VALUES(?,?,?,?) ''',
        'address_range': ''' (name,comments,color,ipaddr_first,ipaddr_last)
              VALUES(?,?,?,?,?) ''',
        'network': ''' (name,comments,color,ip_address)
              VALUES(?,?,?,?) ''',
        'gateway_cluster': ''' (name,comments,color,nodes)
              VALUES(?,?,?,?) ''',
        'network_object_group': ''' (name,comments,color,members)
              VALUES(?,?,?,?) ''',
        'group_with_exception': ''' (name,comments,color,members,exceptions)
              VALUES(?,?,?,?,?) '''
    }
    count_cluster_member = 0
    count_gateway_ckp = 0
    count_connectra = 0
    count_gateway_plain = 0
    count_sofaware_gateway = 0
    count_host_plain = 0
    count_host_ckp = 0
    count_address_range = 0
    count_network = 0
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

    for net_obj_ in root.findall('network_object'):
        class_name = net_obj_.find('Class_Name').text
        name = db_worker.del_nt(net_obj_.find('Name').text)
        comment = db_worker.del_nt(net_obj_.find('comments').text)
        color = db_worker.del_nt(net_obj_.find('color').text)
        logging.info("Now under analyze... " + name)
        j = 0
        if class_name == 'cluster_member':
            net_obj = (name, comment, color) + parser_type1(net_obj_)
            count_cluster_member += 1
            j = 1
        elif class_name == 'gateway_ckp':
            net_obj = (name, comment, color) + parser_type1(net_obj_)
            count_gateway_ckp += 1
            j = 1
        elif class_name == 'connectra':
            net_obj = (name, comment, color) + parser_type1(net_obj_)
            count_connectra += 1
            j = 1
        elif class_name == 'gateway_plain':
            net_obj = (name, comment, color) + parser_type1(net_obj_)
            count_gateway_plain += 1
            j = 1
        elif class_name == 'sofaware_gateway':
            net_obj = (name, comment, color) + parser_type1(net_obj_)
            count_sofaware_gateway += 1
            j = 1
        elif class_name == 'host_plain':
            net_obj = (name, comment, color) + parser_type2(net_obj_)
            count_host_plain += 1
            j = 1
        elif class_name == 'host_ckp':
            net_obj = (name, comment, color) + parser_type2(net_obj_)
            count_host_ckp += 1
            j = 1
        elif class_name == 'address_range':
            net_obj = (name, comment, color) + parser_type3(net_obj_)
            count_address_range += 1
            j = 1
        elif class_name == 'network':
            net_obj = (name, comment, color) + parser_type4(net_obj_)
            count_network += 1
            j = 1
        elif class_name == 'gateway_cluster':
            net_obj = (name, comment, color) + parser_type5(net_obj_)
            count_gateway_cluster += 1
            j = 1
        elif class_name == 'network_object_group':
            members = parser_type6(net_obj_)
            net_obj = (name, comment, color) + members
            count_network_group += 1
            groups_list[name] = len(members[0].split(","))
            j = 1
        elif class_name == 'group_with_exception':
            net_obj = (name, comment, color) + parser_type7(net_obj_)
            count_group_with_exception += 1
            j = 1
        if j == 1:
            db_worker.create_net_obj(conn, net_obj, class_name, net_obj_type_dict[class_name])
            logging.info(net_obj)
    conn.commit()
    output.print_to_xlsx(groups_list, "groups_r77.30.xlsx")
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

    db_worker.create_index_table(conn, "cluster_member", "network_object_index")
    db_worker.create_index_table(conn, "connectra", "network_object_index")
    db_worker.create_index_table(conn, "gateway_ckp", "network_object_index")
    db_worker.create_index_table(conn, "gateway_plain", "network_object_index")
    db_worker.create_index_table(conn, "sofaware_gateway", "network_object_index")
    db_worker.create_index_table(conn, "gateway_cluster", "network_object_index")
    db_worker.create_index_table(conn, "address_range", "network_object_index")
    db_worker.create_index_table(conn, "host_plain", "network_object_index")
    db_worker.create_index_table(conn, "host_ckp", "network_object_index")
    db_worker.create_index_table(conn, "network", "network_object_index")
    db_worker.create_index_table(conn, "group_with_exception", "network_object_index")
    db_worker.create_index_table(conn, "network_object_group", "network_object_index")
    cur = conn.cursor()
    try:
        cur.execute("CREATE UNIQUE INDEX idx_network_object_index ON network_object_index (name)")
    except Error as e:
        logging.warning(e)
        logging.info(str(e))

    f.close()


def create_list_network_object(filepath):
    sql_create_cluster_member_table = """ CREATE TABLE IF NOT EXISTS cluster_member (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         interfaces text
                                     ); """
    sql_create_connectra_table = """ CREATE TABLE IF NOT EXISTS connectra (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         interfaces text
                                     ); """
    sql_create_gateway_ckp_table = """ CREATE TABLE IF NOT EXISTS gateway_ckp (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         interfaces text
                                     ); """
    sql_create_gateway_plain_table = """ CREATE TABLE IF NOT EXISTS gateway_plain (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         interfaces text
                                     ); """
    sql_create_sofaware_gateway_table = """ CREATE TABLE IF NOT EXISTS sofaware_gateway (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         interfaces text
                                     ); """
    sql_create_gateway_cluster_table = """ CREATE TABLE IF NOT EXISTS gateway_cluster (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         nodes text
                                     ); """
    sql_create_address_range_table = """ CREATE TABLE IF NOT EXISTS address_range (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         ipaddr_first text,
                                         ipaddr_last text
                                     ); """
    sql_create_host_plain_table = """ CREATE TABLE IF NOT EXISTS host_plain (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         ip_address text
                                     ); """
    sql_create_host_ckp_table = """ CREATE TABLE IF NOT EXISTS host_ckp (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         ip_address text
                                     ); """
    sql_create_network_table = """ CREATE TABLE IF NOT EXISTS network (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         ip_address text
                                     ); """
    sql_create_group_with_exception_table = """ CREATE TABLE IF NOT EXISTS group_with_exception (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         members text,
                                         exceptions text
                                     ); """
    sql_create_network_object_group_table = """ CREATE TABLE IF NOT EXISTS network_object_group (
                                         name text PRIMARY KEY,
                                         comments text,
                                         color text,
                                         members text
                                     ); """
    sql_create_network_object_index_table = """ CREATE TABLE IF NOT EXISTS network_object_index (
                                         name text PRIMARY KEY,
                                         type text
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
        db_worker.create_table(conn, sql_create_network_object_index_table)
        parse_list_network_object(filepath + "\\network_objects_new.xml", conn)
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
