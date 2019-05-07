from database import db_worker
import xml.etree.ElementTree as ET

import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)


def parse_list_service(filename, conn):
    f = open(filename, 'rU')
    sql_service = ''' (name,comments,type,port)
              VALUES(?,?,?,?) '''
    sql_service_group = ''' (name,comments,members)
              VALUES(?,?,?) '''
    tree_services = ET.parse(filename)
    root_services = tree_services.getroot()
    count_services = 0
    for service_ in root_services.findall('service'):
        # Add to all objects database tcp and udp services as object class service
        if service_.find('Class_Name').text == 'tcp_service' or service_.find('Class_Name').text == 'udp_service':
            name = db_worker.del_nt(service_.find('Name').text)
            comment = db_worker.del_nt(service_.find('comments').text)
            type = db_worker.del_nt(service_.find('type').text)
            port = db_worker.del_nt(service_.find('port').text)
            logging.info("Now under analyze... " + name)
            service = (name, comment, type, port)
            db_worker.create_net_obj(conn, service, "services", sql_service)
            count_services += 1
        # Add to all objects database all other services
        else:
            if service_.find('Class_Name').text != 'service_group':
                name = db_worker.del_nt(service_.find('Name').text)
                type = "other_service"
                comment = db_worker.del_nt(service_.find('comments').text)
                logging.info("Now under analyze... " + name)
                port = None
                service = (name, comment, type, port)
                db_worker.create_net_obj(conn, service, "services", sql_service)

                count_services += 1
    conn.commit()
    # Add to all objects database service groups as lists
    for service_ in root_services.findall('service'):
        if service_.find('Class_Name').text == 'service_group':
            name = db_worker.del_nt(service_.find('Name').text)
            comment = db_worker.del_nt(service_.find('comments').text)
            logging.info("Now under analyze... " + name)
            members = []
            for service_gr_mem in service_.findall('members'):
                elements = service_gr_mem.findall('reference')
                for element in elements:
                    members.append(db_worker.del_nt(element.find('Name').text))
            members_str = " , ".join(members)
            service_group = (name, comment, members_str)
            db_worker.create_net_obj(conn, service_group, "service_groups", sql_service_group)
            count_services += 1
    conn.commit()
    print('Numbers of services and groups = ' + str(count_services))
    f.close()


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
