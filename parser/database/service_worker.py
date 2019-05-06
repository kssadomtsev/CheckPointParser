from sqlite3 import Error
from database import db_worker
import xml.etree.ElementTree as ET

import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)


def create_service(conn, service):
    """
    Create a new service
    :param conn:
    :param service:
    :return:
    """

    sql = ''' INSERT INTO services (name,comments,type,port)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    #   print(service)
    try:
        cur.execute(sql, service)
    except Error as e:
        logging.warning(str(e) + " for entry " + service[0])
    return cur.lastrowid


def create_service_group(conn, service_group):
    """
    Create a new service_group
    :param conn:
    :param service_group:
    :return:
    """

    sql = ''' INSERT INTO service_groups (name,comments,members)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    #   print(service)
    try:
        cur.execute(sql, service_group)
    except Error as e:
        logging.warning(str(e) + " for entry " + service_group[0])
    return cur.lastrowid


def parse_list_service(filename, conn):
    f = open(filename, 'rU')
    #   services=[]
    tree_services = ET.parse(filename)
    root_services = tree_services.getroot()
    #   print(root_services.tag)
    count_services = 0
    for service_ in root_services.findall('service'):
        # Add to all objects database tcp and udp services as object class service
        if service_.find('Class_Name').text == 'tcp_service' or service_.find('Class_Name').text == 'udp_service':
            #  print(service_.find('Name').text, service_.find('comments').text, service_.find('type').text,
            #      service_.find('port').text)
            name = db_worker.del_nt(service_.find('Name').text)
            comment = db_worker.del_nt(service_.find('comments').text)
            type = db_worker.del_nt(service_.find('type').text)
            port = db_worker.del_nt(service_.find('port').text)
            service = (name, comment, type, port)
            #           print(service)
            create_service(conn, service)
            #           services.append(service(name,comment,proto,port))
            # temp_service = service(name, comment, proto, port)
            #  db_obj[name] = temp_service
            count_services += 1
        # Add to all objects database all other services
        else:
            if service_.find('Class_Name').text != 'service_group':
                name = db_worker.del_nt(service_.find('Name').text)
                type = "other_service"
                comment = db_worker.del_nt(service_.find('comments').text)
                port = None
                service = (name, comment, type, port)
                #                print(service)
                create_service(conn, service)
                #               create_service(conn, service)

                #    temp_service = other_service(name, class_name, comment)
                #     db_obj[name] = temp_service
                #    print(name)
                count_services += 1
    #   j = 0
    # At first let's count how many service group we have
    #   for service_ in root_services.findall('service'):
    #      if service_.find('Class_Name').text == 'service_group':
    #         j += 1
    #  print("Count of service group is... " + str(j))
    conn.commit()
    # Add to all objects database service groups as lists
    for service_ in root_services.findall('service'):
        if service_.find('Class_Name').text == 'service_group':
            name = db_worker.del_nt(service_.find('Name').text)
            comment = db_worker.del_nt(service_.find('comments').text)
            members = []
            #               print('Service group = ',name)
            for service_gr_mem in service_.findall('members'):
                elements = service_gr_mem.findall('reference')
                for element in elements:
                    members.append(db_worker.del_nt(element.find('Name').text))
            members_str = " , ".join(members)
            #            print(name, comment, members_str)
            service_group = (name, comment, members_str)
            create_service_group(conn, service_group)
            #                   print (element_name, db_obj[element.find('Name').text])
            #   db_obj[name] = service_group(name, comment, services)
            #                   print (name, db_obj[name], db_obj[name].__class__.__name__)
            count_services += 1
    #            print (db_obj[name])
    conn.commit()
    # for service_ in services:
    #      service_.print_service()
    # Manually add service_any object

    #   db_obj["service_any"] = other_service("service_any", "service_any", "service_any")
    print('Numbers of services and groups = ' + str(count_services))
    f.close()


#   return services


def create_list_service(filepath):
    sql_create_services_table = """ CREATE TABLE IF NOT EXISTS services (
                                         name text PRIMARY KEY,
                                         comments text,
                                         type text,
                                         port text
                                     ); """
    sql_create_service_groups_table = """ CREATE TABLE IF NOT EXISTS service_groups (
                                         name text PRIMARY KEY,
                                         comments text,
                                         members text
                                     ); """
    conn = db_worker.create_connection()
    if conn is not None:
        db_worker.create_table(conn, sql_create_services_table)
        db_worker.create_table(conn, sql_create_service_groups_table)
        parse_list_service(filepath + "\\services_new.xml", conn)
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
