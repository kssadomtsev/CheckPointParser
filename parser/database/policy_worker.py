from database import db_worker
import xml.etree.ElementTree as ET
import logging

logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename="..\\logs\\parser_log.log",
                    level=logging.DEBUG, filemode='w')


def global_condition(table, rule):
    if table == 'security_policy':
        return db_worker.del_nt(rule.find('global_location').text) == 'middle'
    else:
        return db_worker.del_nt(rule.find('global_location').text) == 'before' or db_worker.del_nt(rule.find('global_location').text) == 'after'

def parse_list_security_policy(filename, conn, table):
    f = open(filename, 'rU')
    sql_security_policy = ''' (Rule_Number,section,name,comments,src,src_neg,dst,dst_neg,services,action)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    tree = ET.parse(filename)
    root = tree.getroot()
    print(root)
    count_enabled_rules = 1
    for rule in root.findall('./fw_policie/rule/rule'):
        if rule.find('Class_Name') is not None and rule.find('disabled').text == 'false' and rule.find(
                'time/time/Name').text == 'Any' and global_condition(table, rule):
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
                services.append(service_.find('Name').text)
            if db_worker.del_nt(rule.find('src/op').text) == "not in":
                sources_neg = "True"
            else:
                sources_neg = "False"
            if db_worker.del_nt(rule.find('dst/op').text) == "not in":
                destinations_neg = "True"
            else:
                destinations_neg = "False"
            sources_str = ",".join(sources)
            destinations_str = ",".join(destinations)
            services_str = ",".join(services)
            net_obj = (
                str(count_enabled_rules), "False", name, comments, sources_str, sources_neg, destinations_str,
                destinations_neg, services_str,
                action)
            db_worker.create_net_obj(conn, net_obj, table, sql_security_policy)
            logging.info(net_obj)
            count_enabled_rules += 1
        elif rule.find('header_text') is not None and table == 'security_policy':
            # if db_worker.del_nt(rule.find('global_location').text) == 'before' or db_worker.del_nt(rule.find('global_location').text) == 'after':
            name = db_worker.del_nt(rule.find('header_text').text)
            print(name)
            net_obj = (str(count_enabled_rules), "True", name, "", "", "", "", "", "", "")
            db_worker.create_net_obj(conn, net_obj, table, sql_security_policy)
            logging.info(net_obj)
            count_enabled_rules += 1
    conn.commit()
    logging.info('Numbers of enabled and no time rules and sections  = ' + str(count_enabled_rules))
    print('Numbers of enabled and no time rules and sections = ' + str(count_enabled_rules - 1))


def create_list_security_policy(filepath, table):
    sql_create_security_policy_table = """ CREATE TABLE IF NOT EXISTS """ + table + """ (
                                         Rule_Number text PRIMARY KEY,
                                         section text,
                                         name text,
                                         comments text,
                                         src text,
                                         src_neg text,
                                         dst text,
                                         dst_neg text,
                                         services text,
                                         action text                                         
                                     ); """
    conn = db_worker.create_connection()
    if conn is not None:
        db_worker.create_table(conn, sql_create_security_policy_table)
        parse_list_security_policy(filepath, conn, table)
    else:
        print("Error! cannot create the database connection.")
        logging.warning("Error! cannot create the database connection.")
