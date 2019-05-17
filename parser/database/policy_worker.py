from database import db_worker
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='../logs/parser_log.log',
                    level=logging.DEBUG)


def parse_list_security_policy(filename, conn):
    f = open(filename, 'rU')
    sql_security_policy = ''' (Rule_Number,name,comments,src,dst,services,action)
              VALUES(?,?,?,?,?,?,?) '''
    tree = ET.parse(filename, ET.XMLParser(encoding="cp1251"))
    root = tree.getroot()
    print(root)
    count_enabled_rules = 0
    for rule in root.findall('./fw_policie/rule/rule'):
        if rule.find('Class_Name') is not None and rule.find('disabled').text == 'false' and rule.find('time/time/Name').text == 'Any':
            number = db_worker.del_nt(rule.find('Rule_Number').text)
            name = db_worker.del_nt(rule.find('name').text)
            comments = db_worker.del_nt(rule.find('comments').text)
            action = db_worker.del_nt(rule.find('action/action/Name').text)
            sources = []
            destinations = []
            services = []
            for src in rule.findall('src/members/reference'):
                sources.append(db_worker.del_nt(src.find('Name').text))
            for dst in rule.findall('dst/members/reference'):
                destinations.append(db_worker.del_nt(dst.find('Name').text))
            for service_ in rule.findall('services/members/reference'):
                services.append(db_worker.del_g(db_worker.del_nt(service_.find('Name').text)))
            sources_str = ",".join(sources)
            destinations_str = ",".join(destinations)
            services_str = ",".join(services)
            net_obj = (number, name, comments, sources_str, destinations_str, services_str, action)
            db_worker.create_net_obj(conn, net_obj, 'security_policy', sql_security_policy)
            logging.info(net_obj)
            count_enabled_rules += 1
    conn.commit()
    logging.info('Numbers of enabled and no time rules = ' + str(count_enabled_rules))
    print('Numbers of enabled and no time rules = ' + str(count_enabled_rules))


def create_list_security_policy(filepath):
    sql_create_security_policy_table = """ CREATE TABLE IF NOT EXISTS security_policy (
                                         Rule_Number text PRIMARY KEY,
                                         name text,
                                         comments text,
                                         src text,
                                         dst text,
                                         services text,
                                         action text                                         
                                     ); """
    conn = db_worker.create_connection()
    if conn is not None:
        db_worker.create_table(conn, sql_create_security_policy_table)
        parse_list_security_policy(filepath, conn)
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
